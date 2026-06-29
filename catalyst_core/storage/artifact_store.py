"""Artifact metadata store.

Core artifacts are references, not arbitrary file writers. Layer 1 evidence
collectors may register artifacts by URI; the core stores metadata only.
"""
from __future__ import annotations

from catalyst_core.domain.base import new_id, now_iso, to_json

from .sqlite_store import SQLiteStore


class ArtifactStore:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def register(self, uri: str, kind: str, project: str = "default", metadata: dict | None = None) -> dict:
        artifact = {
            "id": new_id("art"),
            "project": project,
            "uri": uri,
            "kind": kind,
            "metadata": metadata or {},
            "created_at": now_iso(),
        }
        with self.store.transaction() as conn:
            conn.execute(
                """
                INSERT INTO artifacts (id, project, uri, kind, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (artifact["id"], project, uri, kind, to_json(artifact["metadata"]), artifact["created_at"]),
            )
        return artifact

