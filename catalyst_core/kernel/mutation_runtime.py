"""Mutation validation and commit runtime."""
from __future__ import annotations

from catalyst_core.domain.base import dump_model, new_id, now_iso
from catalyst_core.domain.constants import EDGE_TYPES, EVENT_TYPES, OBJECT_TYPES
from catalyst_core.domain.engines import EngineRunRecord
from catalyst_core.domain.events import CoreEvent
from catalyst_core.domain.evidence import EvidenceItem
from catalyst_core.domain.evals import EvalCheck, EvalResult
from catalyst_core.domain.feedback import FeedbackEvent
from catalyst_core.domain.graph import ObjectEdge
from catalyst_core.domain.mutations import CommittedEvents, ProposedMutation, ValidationResult
from catalyst_core.domain.objects import CognitiveObject
from catalyst_core.domain.packets import AgentPacket
from catalyst_core.domain.proof import ProofRecord
from catalyst_core.domain.retrieval import RetrievalRunRecord
from catalyst_core.storage.sqlite_store import SQLiteStore


MUTATION_EVENTS = {
    "evidence.upsert": "evidence.ingested",
    "object.upsert": "object.confirmed",
    "edge.create": "edge.created",
    "engine_run.record": "engine.ran",
    "retrieval.record": "retrieval.ran",
    "packet.record": "packet.compiled",
    "eval_check.upsert": "object.confirmed",
    "eval_result.record": "eval.ran",
    "feedback.record": "feedback.received",
    "proof.record": "proof.created",
    "object_score.update": "confidence.updated",
}


class MutationRuntime:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def validate(self, mutation: ProposedMutation | dict) -> ValidationResult:
        data = dump_model(mutation)
        errors: list[str] = []
        mtype = data.get("type") or ""
        event_type = data.get("event_type") or MUTATION_EVENTS.get(mtype, "")
        payload = data.get("payload") or {}
        if mtype not in MUTATION_EVENTS:
            errors.append(f"unsupported mutation type: {mtype}")
        if event_type not in EVENT_TYPES:
            errors.append(f"unsupported event type: {event_type}")
        if mtype == "object.upsert" and payload.get("type") not in OBJECT_TYPES:
            errors.append(f"unsupported object type: {payload.get('type')}")
        if mtype == "edge.create" and payload.get("type") not in EDGE_TYPES:
            errors.append(f"unsupported edge type: {payload.get('type')}")
        if mtype == "object.upsert" and not payload.get("evidence_ids") and payload.get("type") != "agent_packet":
            errors.append("cognitive objects require evidence_ids")
        return ValidationResult(ok=not errors, errors=errors)

    def commit(self, mutations: list[ProposedMutation | dict]) -> CommittedEvents:
        event_ids: list[str] = []
        mutation_ids: list[str] = []
        with self.store.transaction() as conn:
            for mutation in mutations:
                data = dump_model(mutation)
                data.setdefault("id", new_id("mut"))
                data.setdefault("event_type", MUTATION_EVENTS.get(data.get("type"), ""))
                validation = self.validate(data)
                if not validation.ok:
                    raise ValueError("; ".join(validation.errors))
                event = CoreEvent(
                    id=new_id("evt"),
                    type=data["event_type"],
                    project=data.get("project") or "default",
                    aggregate_id=data.get("aggregate_id") or _aggregate_id(data),
                    aggregate_type=data.get("aggregate_type") or data.get("type") or "",
                    payload=data.get("payload") or {},
                    metadata={
                        **(data.get("metadata") or {}),
                        "mutation_id": data["id"],
                        "engine_id": data.get("engine_id") or "",
                    },
                    idempotency_key=data.get("idempotency_key") or "",
                    created_at=now_iso(),
                )
                event_data = self.store.append_event(conn, event)
                self.store.record_proposed_mutation(conn, data, event_data["id"])
                self._apply(conn, data, event_data["id"])
                event_ids.append(event_data["id"])
                mutation_ids.append(data["id"])
        return CommittedEvents(event_ids=event_ids, mutation_ids=mutation_ids)

    def _apply(self, conn, mutation: dict, event_id: str) -> None:
        payload = mutation.get("payload") or {}
        mtype = mutation.get("type")
        if mtype == "evidence.upsert":
            self.store.upsert_evidence(conn, EvidenceItem.model_validate(payload))
        elif mtype == "object.upsert":
            self.store.upsert_object(conn, CognitiveObject.model_validate(payload), event_id=event_id)
        elif mtype == "edge.create":
            self.store.insert_edge(conn, ObjectEdge.model_validate(payload))
        elif mtype == "engine_run.record":
            self.store.insert_engine_run(conn, EngineRunRecord.model_validate(payload))
        elif mtype == "retrieval.record":
            self.store.insert_retrieval_run(conn, RetrievalRunRecord.model_validate(payload))
        elif mtype == "packet.record":
            self.store.insert_packet(conn, AgentPacket.model_validate(payload))
        elif mtype == "eval_check.upsert":
            self.store.upsert_eval_check(conn, EvalCheck.model_validate(payload))
        elif mtype == "eval_result.record":
            self.store.insert_eval_result(conn, EvalResult.model_validate(payload))
        elif mtype == "feedback.record":
            self.store.insert_feedback_event(conn, FeedbackEvent.model_validate(payload))
        elif mtype == "proof.record":
            self.store.insert_proof_record(conn, ProofRecord.model_validate(payload))
        elif mtype == "object_score.update":
            self.store.update_object_score(
                conn,
                payload.get("object_id") or "",
                mutation.get("project") or payload.get("project") or "default",
                confidence_delta=float(payload.get("confidence_delta") or 0.0),
                retrieval_weight_delta=float(payload.get("retrieval_weight_delta") or 0.0),
                success_delta=int(payload.get("success_delta") or 0),
                failure_delta=int(payload.get("failure_delta") or 0),
                mark_used=bool(payload.get("mark_used")),
            )


def _aggregate_id(mutation: dict) -> str:
    payload = mutation.get("payload") or {}
    return payload.get("id") or payload.get("object_id") or new_id("agg")

