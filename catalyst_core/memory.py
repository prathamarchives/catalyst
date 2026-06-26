"""Memory atoms: durable learned units derived from signals."""
from __future__ import annotations

from pathlib import Path

from . import store

TYPE_BY_SIGNAL = {
    "identity_signal": "identity_signal",
    "context_signal": "fact",
    "cognitive_signal": "decision_rule",
    "behavior_signal": "workflow",
    "direction_signal": "fact",
    "standard_signal": "standard",
    "judgment_signal": "judgment_signal",
    "taste_signal": "taste_signal",
    "voice_signal": "voice_signal",
    "workflow_signal": "workflow",
    "feedback_signal": "preference",
    "execution_signal": "fact",
    "relationship_signal": "fact",
    "environment_signal": "constraint",
    "agent_interface_signal": "workflow",
}


def _norm(text: str) -> str:
    return " ".join((text or "").lower().split())


def list_memories(project: str | None = None, limit: int = 200, state_root: Path = store.STATE_ROOT) -> list[dict]:
    return store.latest(store.filter_rows(store.read_jsonl("memories/memories.jsonl", state_root), project), limit)


def signal_to_memory(signal: dict) -> dict:
    now = store.now_iso()
    return {
        "id": store.new_id("mem"),
        "type": TYPE_BY_SIGNAL.get(signal.get("type"), "fact"),
        "text": signal.get("text") or "",
        "source_signal_ids": [signal["id"]],
        "source_event_ids": [signal["source_event_id"]],
        "confidence": signal.get("confidence", 0.5),
        "maturity": 1,
        "status": "active",
        "project": signal.get("project") or "default",
        "target_brain": signal.get("target_brain") or "context",
        "created_at": now,
        "updated_at": now,
    }


def create_or_merge_memory(signal: dict, state_root: Path = store.STATE_ROOT) -> dict:
    existing = store.read_jsonl("memories/memories.jsonl", state_root)
    needle = _norm(signal.get("text") or "")
    for mem in existing:
        if mem.get("project") == (signal.get("project") or "default") and _norm(mem.get("text") or "") == needle:
            mem = dict(mem)
            mem["source_signal_ids"] = sorted(set(mem.get("source_signal_ids", []) + [signal["id"]]))
            mem["source_event_ids"] = sorted(set(mem.get("source_event_ids", []) + [signal["source_event_id"]]))
            mem["confidence"] = max(float(mem.get("confidence", 0.0)), float(signal.get("confidence", 0.5)))
            mem["maturity"] = min(5, int(mem.get("maturity", 1)) + 1)
            mem["updated_at"] = store.now_iso()
            store.append_jsonl("memories/memories.jsonl", mem, state_root)
            return {**mem, "merged": True}
    mem = signal_to_memory(signal)
    store.append_jsonl("memories/memories.jsonl", mem, state_root)
    return {**mem, "merged": False}


def search_memories(query: str, project: str | None = None, limit: int = 20,
                    state_root: Path = store.STATE_ROOT) -> list[dict]:
    terms = [t for t in _norm(query).split() if len(t) > 2]
    rows = list_memories(project=project, limit=1000, state_root=state_root)
    scored = []
    for mem in rows:
        hay = _norm(" ".join(str(mem.get(k, "")) for k in ("text", "type", "target_brain")))
        score = sum(1 for t in terms if t in hay)
        if score or not terms:
            scored.append((score, mem))
    return [m for _, m in sorted(scored, key=lambda x: (x[0], x[1].get("updated_at", "")), reverse=True)[:limit]]


def compact_profile(project: str | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    rows = list_memories(project=project, limit=500, state_root=state_root)
    groups: dict[str, list[str]] = {}
    for mem in rows:
        groups.setdefault(mem.get("target_brain") or "context", []).append(mem.get("text") or "")
    return {
        "project": project or "all",
        "memory_count": len(rows),
        "profile_summary": {k: v[:5] for k, v in sorted(groups.items())},
    }

