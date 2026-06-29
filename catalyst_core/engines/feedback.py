from __future__ import annotations

from catalyst_core.domain.base import new_id, now_iso
from catalyst_core.domain.constants import BAD_SAAS_TERMS
from catalyst_core.domain.engines import EngineInput
from catalyst_core.domain.evidence import EvidenceItem
from catalyst_core.domain.evals import EvalCheck
from catalyst_core.domain.feedback import FeedbackEvent
from catalyst_core.domain.graph import ObjectEdge
from catalyst_core.domain.mutations import ProposedMutation
from catalyst_core.domain.objects import CognitiveObject
from catalyst_core.policies.confidence import confidence_from_evidence

from .base import BaseEngine
from .specs import ENGINE_SPECS


class FeedbackLearningEngine(BaseEngine):
    spec = next(s for s in ENGINE_SPECS if s.id == "eval_feedback_engine")

    def run(self, engine_input: EngineInput) -> list[ProposedMutation]:
        data = engine_input.data
        project = engine_input.project
        packet = data.get("packet") or {}
        task = data.get("task") or packet.get("task") or ""
        output = data.get("output") or ""
        feedback_text = data.get("feedback") or ""
        feedback_type = data.get("feedback_type") or "rejection"
        now = now_iso()
        feedback_id = new_id("fb")
        evidence_id = new_id("ev")
        evidence = EvidenceItem(
            id=evidence_id,
            project=project,
            content=f"Task: {task}\nOutput: {output}\nFeedback: {feedback_text}",
            source="feedback",
            source_type="user_feedback",
            scope=packet.get("scope") or task,
            audience=packet.get("audience") or "",
            task_type=packet.get("task_type") or _task_type(task),
            source_strength=0.9,
            created_at=now,
            metadata={"packet_id": data.get("packet_id") or ""},
        )
        feedback = FeedbackEvent(
            id=feedback_id,
            project=project,
            packet_id=data.get("packet_id") or "",
            eval_result_id=data.get("eval_result_id") or "",
            task=task,
            output=output,
            feedback=feedback_text,
            feedback_type=feedback_type,
            created_at=now,
        )
        objects = _objects_from_feedback(project, evidence_id, task, output, feedback_text, now)
        eval_check = _eval_check(project, objects["eval_check"].id, objects["anti_pattern"].id, now)
        mutations: list[ProposedMutation] = [
            _mutation("evidence.upsert", "evidence.ingested", project, evidence.id, "evidence_item", evidence.model_dump(), self.spec.id),
            _mutation("feedback.record", "feedback.received", project, feedback.id, "feedback_event", feedback.model_dump(), self.spec.id),
        ]
        for obj in objects.values():
            mutations.append(_mutation("object.upsert", "object.confirmed", project, obj.id, "cognitive_object", obj.model_dump(), self.spec.id))
        mutations.append(_mutation("eval_check.upsert", "object.confirmed", project, eval_check.id, "eval_check", eval_check.model_dump(), self.spec.id))
        edge_pairs = [
            (evidence.id, objects["taste_delta"].id, "extracted_from"),
            (evidence.id, objects["judgment_atom"].id, "extracted_from"),
            (feedback.id, objects["taste_delta"].id, "updated_by"),
            (objects["taste_delta"].id, objects["anti_pattern"].id, "supports"),
            (objects["judgment_atom"].id, objects["standard_atom"].id, "supports"),
            (objects["anti_pattern"].id, eval_check.id, "evaluated_by"),
            (objects["standard_atom"].id, eval_check.id, "supports"),
        ]
        for from_id, to_id, edge_type in edge_pairs:
            edge = ObjectEdge(
                id=new_id("edge"),
                project=project,
                from_id=from_id,
                to_id=to_id,
                type=edge_type,
                confidence=0.9,
                created_at=now,
                metadata={"feedback_event_id": feedback.id},
            )
            mutations.append(_mutation("edge.create", "edge.created", project, edge.id, "object_edge", edge.model_dump(), self.spec.id))
        for obj in objects.values():
            mutations.append(_mutation(
                "object_score.update",
                "retrieval_weight.updated",
                project,
                obj.id,
                "object_score",
                {
                    "object_id": obj.id,
                    "project": project,
                    "confidence_delta": 0.08,
                    "retrieval_weight_delta": 0.35 if obj.type in {"anti_pattern", "standard_atom", "eval_check"} else 0.2,
                    "success_delta": 0,
                    "failure_delta": 0,
                },
                self.spec.id,
            ))
        return mutations


def _objects_from_feedback(project: str, evidence_id: str, task: str, output: str, feedback: str, now: str) -> dict[str, CognitiveObject]:
    generic = _mentions_generic_saas(output, feedback)
    scope = task or "unspecified task"
    task_type = _task_type(task)
    base_conf = confidence_from_evidence(0.9, confirmations=1)
    if generic:
        anti = "Avoid generic SaaS slop: do not use sanitized productivity-platform language for Catalyst; make the specific judgment, taste, retrieval, eval, and feedback-learning mechanism visible."
        standard = "Catalyst public copy must name the cognitive kernel: memory, judgment, taste, retrieval, eval, feedback learning, and proof."
        taste = "The user rejects generic SaaS framing for Catalyst and prefers concrete mechanism-first language."
        judgment = "Reject Catalyst output that could describe any AI productivity platform."
        check = "Fail output that uses vague productivity or seamless workflow framing without Catalyst's cognitive kernel."
    else:
        anti = f"Avoid repeating rejected pattern: {feedback.strip()}"
        standard = f"Future work should incorporate this correction: {feedback.strip()}"
        taste = f"Preference delta from feedback: {feedback.strip()}"
        judgment = f"Judgment rule from feedback: {feedback.strip()}"
        check = f"Check future output against correction: {feedback.strip()}"
    return {
        "taste_delta": CognitiveObject(
            id=new_id("obj"),
            type="taste_delta",
            content=taste,
            scope=scope,
            project=project,
            task_type=task_type,
            confidence=base_conf,
            source_strength=0.9,
            evidence_ids=[evidence_id],
            memory_family="preference",
            created_at=now,
            updated_at=now,
        ),
        "judgment_atom": CognitiveObject(
            id=new_id("obj"),
            type="judgment_atom",
            content=judgment,
            scope=scope,
            project=project,
            task_type=task_type,
            confidence=base_conf,
            source_strength=0.9,
            evidence_ids=[evidence_id],
            memory_family="semantic",
            created_at=now,
            updated_at=now,
        ),
        "anti_pattern": CognitiveObject(
            id=new_id("obj"),
            type="anti_pattern",
            content=anti,
            scope=scope,
            project=project,
            task_type=task_type,
            confidence=base_conf,
            source_strength=0.9,
            evidence_ids=[evidence_id],
            memory_family="negative",
            created_at=now,
            updated_at=now,
        ),
        "standard_atom": CognitiveObject(
            id=new_id("obj"),
            type="standard_atom",
            content=standard,
            scope=scope,
            project=project,
            task_type=task_type,
            confidence=base_conf,
            source_strength=0.9,
            evidence_ids=[evidence_id],
            memory_family="procedural",
            created_at=now,
            updated_at=now,
        ),
        "eval_check": CognitiveObject(
            id=new_id("obj"),
            type="eval_check",
            content=check,
            scope=scope,
            project=project,
            task_type=task_type,
            confidence=base_conf,
            source_strength=0.9,
            evidence_ids=[evidence_id],
            memory_family="procedural",
            created_at=now,
            updated_at=now,
        ),
    }


def _eval_check(project: str, check_object_id: str, anti_pattern_id: str, now: str) -> EvalCheck:
    return EvalCheck(
        id=check_object_id,
        project=project,
        object_id=anti_pattern_id,
        name="Reject generic SaaS framing",
        check_type="negative_constraint",
        content="Output fails if it relies on generic SaaS/productivity language instead of Catalyst's cognitive kernel.",
        failure_terms=sorted(BAD_SAAS_TERMS),
        severity="high",
        created_at=now,
    )


def _mentions_generic_saas(output: str, feedback: str) -> bool:
    text = f"{output}\n{feedback}".lower()
    return any(term in text for term in BAD_SAAS_TERMS) or "slop" in text


def _task_type(task: str) -> str:
    low = (task or "").lower()
    if "copy" in low or "landing" in low or "post" in low:
        return "writing"
    if "design" in low:
        return "design"
    return "general"


def _mutation(mtype: str, event_type: str, project: str, aggregate_id: str, aggregate_type: str,
              payload: dict, engine_id: str) -> ProposedMutation:
    return ProposedMutation(
        id=new_id("mut"),
        type=mtype,
        event_type=event_type,
        project=project,
        aggregate_id=aggregate_id,
        aggregate_type=aggregate_type,
        payload=payload,
        engine_id=engine_id,
    )

