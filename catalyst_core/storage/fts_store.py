"""FTS helper boundary."""
from __future__ import annotations

from .sqlite_store import SQLiteStore


class FTSStore:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def search_objects(self, project: str, query: str, limit: int = 20) -> list[dict]:
        return self.store.search_fts(project, query, limit)

