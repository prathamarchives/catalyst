"""Event capture: raw interactions are the source of truth."""
from __future__ import annotations

from pathlib import Path

from . import store

EVENT_TYPES = {
    "task_started",
    "task_completed",
    "feedback",
    "correction",
    "approval",
    "rejection",
    "user_statement",
    "memory_request",
    "review_result",
}


def normalize_event(event: dict) -> dict:
    data = dict(event or {})
    data.setdefault("id", store.new_id("evt"))
    data["type"] = data.get("type") if data.get("type") in EVENT_TYPES else "user_statement"
    data.setdefault("project", "default")
    data.setdefault("agent", "unknown")
    data.setdefault("task", "")
    data.setdefault("input", "")
    data.setdefault("output", "")
    data.setdefault("user_feedback", "")
    data.setdefault("outcome", "")
    data.setdefault("metadata", {})
    data.setdefault("created_at", store.now_iso())
    if not isinstance(data["metadata"], dict):
        data["metadata"] = {"value": str(data["metadata"])}
    return data


def append_event(event: dict, state_root: Path = store.STATE_ROOT) -> dict:
    return store.append_jsonl("events/events.jsonl", normalize_event(event), state_root)


def list_events(project: str | None = None, limit: int = 100, state_root: Path = store.STATE_ROOT) -> list[dict]:
    return store.latest(store.filter_rows(store.read_jsonl("events/events.jsonl", state_root), project), limit)

