"""Persona sub-brain registry and memory routing."""
from __future__ import annotations

from pathlib import Path

from . import memory, store

SUBBRAIN_REGISTRY = {
    "core": {"folder": "core", "default_file": "persona-summary.md"},
    "identity": {"folder": "identity", "default_file": "identity-spine.md"},
    "context": {"folder": "context", "default_file": "important-facts.md"},
    "cognition": {"folder": "cognition", "default_file": "thinking-patterns.md"},
    "behavior": {"folder": "behavior", "default_file": "work-patterns.md"},
    "direction": {"folder": "direction", "default_file": "current-priorities.md"},
    "standards": {"folder": "standards", "default_file": "general-standards.md"},
    "judgment": {"folder": "judgment", "default_file": "approval-logic.md"},
    "taste": {"folder": "taste", "default_file": "taste-principles.md"},
    "voice": {"folder": "voice", "default_file": "voice-spine.md"},
    "workflow": {"folder": "workflow", "default_file": "task-patterns.md"},
    "memory": {"folder": "memory", "default_file": "semantic-memory.jsonl"},
    "feedback": {"folder": "feedback", "default_file": "recurring-feedback.md"},
    "relationships": {"folder": "relationships", "default_file": "people.md"},
    "execution": {"folder": "execution", "default_file": "next-actions.md"},
    "environment": {"folder": "environment", "default_file": "constraints.md"},
    "agent-interface": {"folder": "agent-interface", "default_file": "agent-contract.md"},
}

FILE_BY_MEMORY_TYPE = {
    "standard": ("standards", "general-standards.md"),
    "rejection": ("judgment", "rejection-logic.md"),
    "approval": ("judgment", "approval-logic.md"),
    "workflow": ("workflow", "task-patterns.md"),
    "decision_rule": ("judgment", "decision-boundaries.md"),
    "taste_signal": ("taste", "taste-principles.md"),
    "voice_signal": ("voice", "voice-spine.md"),
    "identity_signal": ("identity", "identity-spine.md"),
    "judgment_signal": ("judgment", "shipping-rules.md"),
    "constraint": ("environment", "constraints.md"),
    "open_question": ("core", "current-state.md"),
}


def get_subbrain_registry() -> dict:
    return dict(SUBBRAIN_REGISTRY)


def route_memory(mem: dict) -> list[dict]:
    brain = mem.get("target_brain") or FILE_BY_MEMORY_TYPE.get(mem.get("type"), ("context", ""))[0]
    if brain not in SUBBRAIN_REGISTRY:
        brain = FILE_BY_MEMORY_TYPE.get(mem.get("type"), ("core", ""))[0]
    _, default_file = FILE_BY_MEMORY_TYPE.get(
        mem.get("type"),
        (brain, SUBBRAIN_REGISTRY.get(brain, SUBBRAIN_REGISTRY["core"])["default_file"]),
    )
    node = {
        "id": store.new_id("node"),
        "memory_id": mem["id"],
        "brain": brain,
        "section": default_file,
        "priority": max(1, int(round(float(mem.get("confidence", 0.5)) * 5))),
        "maturity": mem.get("maturity", 1),
        "confidence": mem.get("confidence", 0.5),
        "source_event_ids": mem.get("source_event_ids", []),
        "related_nodes": [],
        "project": mem.get("project") or "default",
        "created_at": store.now_iso(),
    }
    return [node]


def append_persona_nodes(nodes: list[dict], state_root: Path = store.STATE_ROOT) -> list[dict]:
    return [store.append_jsonl("persona/persona_nodes.jsonl", n, state_root) for n in nodes]


def list_persona_nodes(project: str | None = None, state_root: Path = store.STATE_ROOT) -> list[dict]:
    return store.filter_rows(store.read_jsonl("persona/persona_nodes.jsonl", state_root), project)


def get_subbrain_status(project: str | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    nodes = list_persona_nodes(project, state_root)
    mem_by_id = {m["id"]: m for m in memory.list_memories(project, limit=1000, state_root=state_root)}
    status = {}
    for brain in SUBBRAIN_REGISTRY:
        owned = [n for n in nodes if n.get("brain") == brain]
        confidences = [float(n.get("confidence", 0.0)) for n in owned]
        maturity = [int(mem_by_id.get(n.get("memory_id"), {}).get("maturity", n.get("maturity", 1))) for n in owned]
        status[brain] = {
            "nodes": len(owned),
            "avg_confidence": round(sum(confidences) / len(confidences), 2) if confidences else 0.0,
            "avg_maturity": round(sum(maturity) / len(maturity), 2) if maturity else 0.0,
            "state": "empty" if not owned else "forming" if len(owned) < 3 else "active",
        }
    return status

