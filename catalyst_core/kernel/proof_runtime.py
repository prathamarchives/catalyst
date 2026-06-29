"""Proof runtime."""
from __future__ import annotations

from catalyst_core.domain.base import new_id, now_iso
from catalyst_core.domain.mutations import ProposedMutation
from catalyst_core.domain.proof import ProofRecord
from catalyst_core.storage.sqlite_store import SQLiteStore

from .mutation_runtime import MutationRuntime


class ProofRuntime:
    def __init__(self, store: SQLiteStore, mutations: MutationRuntime):
        self.store = store
        self.mutations = mutations

    def link_latest_feedback_to_packet(self, project: str, after_packet_id: str, object_ids: list[str]) -> dict | None:
        feedback = self.store.list_feedback(project, limit=10)
        if not feedback:
            return None
        latest = feedback[0]
        before = latest.get("packet_id") or ""
        if not before or before == after_packet_id:
            return None
        existing = self.store.fetch_one(
            """
            SELECT id FROM proof_records
            WHERE project = ? AND before_packet_id = ? AND feedback_event_id = ? AND after_packet_id = ?
            """,
            (project, before, latest["id"], after_packet_id),
        )
        if existing:
            return existing
        proof = ProofRecord(
            id=new_id("proof"),
            project=project,
            before_packet_id=before,
            feedback_event_id=latest["id"],
            after_packet_id=after_packet_id,
            created_object_ids=object_ids,
            claim="Feedback changed the future packet retrieval set.",
            created_at=now_iso(),
            metadata={"feedback": latest.get("feedback") or ""},
        )
        mutation = ProposedMutation(
            id=new_id("mut"),
            type="proof.record",
            event_type="proof.created",
            project=project,
            aggregate_id=proof.id,
            aggregate_type="proof_record",
            payload=proof.model_dump(),
            engine_id="proof_runtime",
        )
        self.mutations.commit([mutation])
        return proof.model_dump()

    def list(self, project: str = "default") -> list[dict]:
        return self.store.list_proofs(project)

