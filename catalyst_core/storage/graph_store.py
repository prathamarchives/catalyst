"""Graph read helpers over the relational edge table."""
from __future__ import annotations

from collections import defaultdict, deque

from .sqlite_store import SQLiteStore


class GraphStore:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def degree(self, project: str, node_id: str) -> int:
        rows = self.store.fetch_all(
            "SELECT COUNT(*) AS n FROM object_edges WHERE project = ? AND (from_id = ? OR to_id = ?)",
            (project, node_id, node_id),
        )
        return int(rows[0]["n"]) if rows else 0

    def paths(self, project: str, start_id: str, end_id: str, max_depth: int = 3) -> list[dict]:
        edges = self.store.list_edges(project)
        by_from: dict[str, list[dict]] = defaultdict(list)
        for edge in edges:
            by_from[edge["from_id"]].append(edge)
        found: list[dict] = []
        q = deque([(start_id, [start_id], [])])
        while q:
            node, nodes, edge_ids = q.popleft()
            if len(edge_ids) >= max_depth:
                continue
            for edge in by_from.get(node, []):
                nxt = edge["to_id"]
                if nxt in nodes:
                    continue
                next_nodes = nodes + [nxt]
                next_edges = edge_ids + [edge["id"]]
                if nxt == end_id:
                    found.append({"start_id": start_id, "end_id": end_id, "node_ids": next_nodes, "edge_ids": next_edges})
                else:
                    q.append((nxt, next_nodes, next_edges))
        return found

    def graph(self, project: str = "default") -> dict:
        objects = self.store.list_objects(project, status=None)
        edges = self.store.list_edges(project)
        return {
            "project": project,
            "nodes": [
                {
                    "id": obj["id"],
                    "type": obj["type"],
                    "label": (obj.get("content") or "")[:96],
                    "status": obj.get("status"),
                    "confidence": obj.get("confidence"),
                }
                for obj in objects
            ],
            "edges": edges,
        }

