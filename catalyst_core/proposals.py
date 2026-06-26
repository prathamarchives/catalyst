"""Safe update proposals. Important changes are proposed, not silently applied."""
from __future__ import annotations

from pathlib import Path

from . import store


def create_proposal(target_file: str, proposed_change: str, reason: str,
                    source_event_id: str | None = None, source_memory_id: str | None = None,
                    target_brain: str | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    proposal = {
        "id": store.new_id("prop"),
        "target_file": target_file,
        "target_brain": target_brain or "",
        "source_memory_id": source_memory_id or "",
        "source_event_id": source_event_id or "",
        "proposed_change": proposed_change,
        "reason": reason,
        "status": "pending",
        "created_at": store.now_iso(),
    }
    return store.append_jsonl("proposals/proposals.jsonl", proposal, state_root)


def list_proposals(status: str | None = None, state_root: Path = store.STATE_ROOT) -> list[dict]:
    rows = store.read_jsonl("proposals/proposals.jsonl", state_root)
    if status:
        rows = [r for r in rows if r.get("status") == status]
    return store.latest(rows, 200)


def _status_update(pid: str, status: str, state_root: Path) -> dict:
    rows = store.read_jsonl("proposals/proposals.jsonl", state_root)
    for row in rows:
        if row.get("id") == pid:
            updated = {**row, "status": status, "updated_at": store.now_iso()}
            store.append_jsonl("proposals/proposals.jsonl", updated, state_root)
            return updated
    return {"error": f"proposal not found: {pid}"}


def apply_proposal(id: str, state_root: Path = store.STATE_ROOT) -> dict:
    return _status_update(id, "applied", state_root)


def reject_proposal(id: str, state_root: Path = store.STATE_ROOT) -> dict:
    return _status_update(id, "rejected", state_root)

