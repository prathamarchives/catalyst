"""Cognitive graph read model."""
from __future__ import annotations

from catalyst_core.storage.graph_store import GraphStore
from catalyst_core.storage.sqlite_store import SQLiteStore


class CognitiveGraph:
    def __init__(self, store: SQLiteStore):
        self.store = store
        self.graph_store = GraphStore(store)

    def graph(self, project: str = "default") -> dict:
        return self.graph_store.graph(project)

    def paths(self, project: str, start_id: str, end_id: str) -> list[dict]:
        return self.graph_store.paths(project, start_id, end_id)

    def degree(self, project: str, node_id: str) -> int:
        return self.graph_store.degree(project, node_id)

