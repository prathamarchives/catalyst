"""Agent trace storage."""
from __future__ import annotations

from pathlib import Path

from . import store


def append_trace(trace: dict, state_root: Path = store.STATE_ROOT) -> dict:
    row = dict(trace or {})
    row.setdefault("id", store.new_id("trace"))
    row.setdefault("agent", "unknown")
    row.setdefault("project", "default")
    row.setdefault("task", "")
    row.setdefault("recall_packet_id", "")
    row.setdefault("output_summary", "")
    row.setdefault("capture_event_id", "")
    row.setdefault("judgment_result_id", "")
    row.setdefault("memory_updates", [])
    row.setdefault("created_at", store.now_iso())
    return store.append_jsonl("traces/traces.jsonl", row, state_root)


def list_traces(project: str | None = None, limit: int = 50, state_root: Path = store.STATE_ROOT) -> list[dict]:
    return store.latest(store.filter_rows(store.read_jsonl("traces/traces.jsonl", state_root), project), limit)

