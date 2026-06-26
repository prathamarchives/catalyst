"""Rule-based signal extraction from raw events."""
from __future__ import annotations

import re
from pathlib import Path

from . import store

SIGNAL_TYPES = {
    "identity_signal",
    "context_signal",
    "cognitive_signal",
    "behavior_signal",
    "direction_signal",
    "standard_signal",
    "judgment_signal",
    "taste_signal",
    "voice_signal",
    "workflow_signal",
    "feedback_signal",
    "execution_signal",
    "relationship_signal",
    "environment_signal",
    "agent_interface_signal",
}

TARGET_BY_SIGNAL = {
    "identity_signal": "identity",
    "context_signal": "context",
    "cognitive_signal": "cognition",
    "behavior_signal": "behavior",
    "direction_signal": "direction",
    "standard_signal": "standards",
    "judgment_signal": "judgment",
    "taste_signal": "taste",
    "voice_signal": "voice",
    "workflow_signal": "workflow",
    "feedback_signal": "feedback",
    "execution_signal": "execution",
    "relationship_signal": "relationships",
    "environment_signal": "environment",
    "agent_interface_signal": "agent-interface",
}


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())[:500]


def _candidate_text(event: dict) -> str:
    return "\n".join(str(event.get(k) or "") for k in ("task", "input", "output", "user_feedback", "outcome"))


def _signal_type(text: str, event_type: str) -> tuple[str, str]:
    low = text.lower()
    if event_type in {"feedback", "correction"} or any(w in low for w in ("too ", "stop ", "don't", "do not", "instead", "never")):
        return "feedback_signal", "feedback"
    if event_type == "approval" or any(w in low for w in ("approved", "ship this", "good", "liked")):
        return "judgment_signal", "judgment"
    if event_type == "rejection" or any(w in low for w in ("reject", "never ship", "bad", "wrong")):
        return "judgment_signal", "judgment"
    if any(w in low for w in ("standard", "quality", "bar", "must", "should")):
        return "standard_signal", "standards"
    if any(w in low for w in ("taste", "feels", "cringe", "like this", "dislike")):
        return "taste_signal", "taste"
    if any(w in low for w in ("voice", "tone", "sound", "phrasing", "words")):
        return "voice_signal", "voice"
    if any(w in low for w in ("workflow", "process", "loop", "always do", "step")):
        return "workflow_signal", "workflow"
    if any(w in low for w in ("goal", "priority", "roadmap", "deadline", "money")):
        return "direction_signal", "direction"
    if any(w in low for w in ("agent", "mcp", "context budget", "tool")):
        return "agent_interface_signal", "agent-interface"
    if any(w in low for w in ("machine", "local", "privacy", "risk", "constraint")):
        return "environment_signal", "environment"
    return "context_signal", "context"


def extract_signals(event: dict) -> list[dict]:
    text = _clean(event.get("user_feedback") or event.get("outcome") or event.get("output") or event.get("input") or event.get("task"))
    if not text:
        return []
    stype, target = _signal_type(_candidate_text(event), event.get("type") or "")
    signal = {
        "id": store.new_id("sig"),
        "source_event_id": event["id"],
        "project": event.get("project") or "default",
        "type": stype,
        "text": text,
        "confidence": 0.72 if stype != "context_signal" else 0.55,
        "target_brain": target,
        "status": "candidate",
        "created_at": store.now_iso(),
    }
    return [signal]


def append_signals(signals: list[dict], state_root: Path = store.STATE_ROOT) -> list[dict]:
    return [store.append_jsonl("signals/signals.jsonl", s, state_root) for s in signals]


def list_signals(project: str | None = None, limit: int = 100, state_root: Path = store.STATE_ROOT) -> list[dict]:
    return store.latest(store.filter_rows(store.read_jsonl("signals/signals.jsonl", state_root), project), limit)

