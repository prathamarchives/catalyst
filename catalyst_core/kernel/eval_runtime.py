"""Evaluation runtime for packets and outputs."""
from __future__ import annotations

from catalyst_core.domain.base import new_id, now_iso
from catalyst_core.domain.constants import BAD_SAAS_TERMS
from catalyst_core.domain.evals import EvalResult
from catalyst_core.domain.graph import ObjectEdge
from catalyst_core.domain.mutations import ProposedMutation
from catalyst_core.policies.eval_scoring import score_from_failures, verdict
from catalyst_core.storage.sqlite_store import SQLiteStore

from .mutation_runtime import MutationRuntime


class EvalRuntime:
    def __init__(self, store: SQLiteStore, mutations: MutationRuntime):
        self.store = store
        self.mutations = mutations

    def evaluate(self, packet_id: str, output: str, project: str = "default") -> dict:
        packet = self.store.get_packet(packet_id)
        if not packet:
            raise ValueError(f"unknown packet_id: {packet_id}")
        objects = [self.store.get_object(oid) for oid in packet.get("object_ids", [])]
        objects = [o for o in objects if o]
        checks = self.store.list_eval_checks(project)
        checks_by_id = {c["id"]: c for c in checks}
        relevant_checks = [checks_by_id[cid] for cid in packet.get("eval_check_ids", []) if cid in checks_by_id]
        failed: list[str] = []
        passed: list[str] = []
        violated_objects: list[str] = []
        issues: list[str] = []
        low = (output or "").lower()
        for obj in objects:
            if obj.get("type") == "anti_pattern" and _violates_anti_pattern(low, obj.get("content") or ""):
                violated_objects.append(obj["id"])
                issues.append(f"Output violates anti-pattern: {obj['content']}")
        for check in relevant_checks:
            terms = [t.lower() for t in check.get("failure_terms", [])]
            hit = any(t and t in low for t in terms)
            if hit:
                failed.append(check["id"])
                if check.get("object_id"):
                    violated_objects.append(check["object_id"])
                issues.append(check.get("content") or check.get("name") or "eval check failed")
            else:
                passed.append(check["id"])
        unique_violations = sorted(set(violated_objects))
        score = score_from_failures(max(1, len(relevant_checks) + len([o for o in objects if o.get("type") == "anti_pattern"])), len(failed) + len(unique_violations))
        result = EvalResult(
            id=new_id("eval"),
            project=project,
            packet_id=packet_id,
            task=packet.get("task") or "",
            output=output or "",
            verdict=verdict(score, len(failed) + len(unique_violations)),
            score=score,
            passed_check_ids=passed,
            failed_check_ids=failed,
            violated_object_ids=unique_violations,
            issues=issues,
            created_at=now_iso(),
        )
        mutations: list[ProposedMutation] = [
            ProposedMutation(
                id=new_id("mut"),
                type="eval_result.record",
                event_type="eval.ran",
                project=project,
                aggregate_id=result.id,
                aggregate_type="eval_result",
                payload=result.model_dump(),
                engine_id="eval_feedback_engine",
            ),
            ProposedMutation(
                id=new_id("mut"),
                type="edge.create",
                event_type="edge.created",
                project=project,
                aggregate_id=new_id("edge"),
                aggregate_type="object_edge",
                payload=ObjectEdge(
                    id=new_id("edge"),
                    project=project,
                    from_id=packet_id,
                    to_id=result.id,
                    type="evaluated_by",
                    confidence=1.0,
                    created_at=now_iso(),
                    metadata={"verdict": result.verdict},
                ).model_dump(),
                engine_id="eval_feedback_engine",
            ),
        ]
        for oid in packet.get("object_ids", []):
            mutations.append(ProposedMutation(
                id=new_id("mut"),
                type="object_score.update",
                event_type="retrieval_weight.updated",
                project=project,
                aggregate_id=oid,
                aggregate_type="object_score",
                payload={
                    "object_id": oid,
                    "project": project,
                    "success_delta": 1 if result.verdict == "ship" else 0,
                    "failure_delta": 1 if oid in unique_violations else 0,
                    "retrieval_weight_delta": -0.05 if oid in unique_violations else 0.03,
                },
                engine_id="eval_feedback_engine",
            ))
        self.mutations.commit(mutations)
        return result.model_dump()


def _violates_anti_pattern(output_low: str, content: str) -> bool:
    content_low = content.lower()
    if any(term in output_low for term in BAD_SAAS_TERMS):
        if "generic" in content_low or "saas" in content_low or "productivity" in content_low:
            return True
    return False

