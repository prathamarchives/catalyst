"""Immutable event log facade."""
from __future__ import annotations

from catalyst_core.domain.events import CoreEvent
from catalyst_core.storage.sqlite_store import SQLiteStore


class EventLog:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def append(self, event: CoreEvent) -> dict:
        with self.store.transaction() as conn:
            return self.store.append_event(conn, event)

    def list(self, project: str = "default", limit: int = 200) -> list[dict]:
        return self.store.list_events(project, limit)

    def count(self, project: str = "default") -> int:
        return self.store.get_event_count(project)

