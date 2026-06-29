"""Contradiction and scope runtime."""
from __future__ import annotations

from catalyst_core.domain.base import new_id, now_iso
from catalyst_core.domain.graph import ObjectEdge
from catalyst_core.domain.mutations import ProposedMutation
from catalyst_core.storage.sqlite_store import SQLiteStore

from .mutation_runtime import MutationRuntime


class ContradictionRuntime:
    def __init__(self, store: SQLiteStore, mutations: MutationRuntime):
        self.store = store
        self.mutations = mutations

    def mark_contradiction(self, from_id: str, to_id: str, project: str = "default", scope: str = "") -> dict:
        edge = ObjectEdge(
            id=new_id("edge"),
            project=project,
            from_id=from_id,
            to_id=to_id,
            type="contradicts",
            confidence=0.8,
            created_at=now_iso(),
            metadata={"scope": scope},
        )
        mutation = ProposedMutation(
            id=new_id("mut"),
            type="edge.create",
            event_type="edge.created",
            project=project,
            aggregate_id=edge.id,
            aggregate_type="object_edge",
            payload=edge.model_dump(),
            engine_id="contradiction_scope_engine",
        )
        self.mutations.commit([mutation])
        return edge.model_dump()

