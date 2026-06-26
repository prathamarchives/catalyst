"""Recall packet engine: compact context before agent work."""
from __future__ import annotations

from pathlib import Path

from . import memory, store, subbrains

TASK_ROUTES = {
    "writing": ["core", "voice", "standards", "judgment", "taste", "feedback"],
    "product": ["core", "direction", "standards", "judgment", "workflow", "cognition"],
    "strategy": ["core", "direction", "judgment", "cognition", "standards"],
    "code": ["context", "workflow", "standards", "environment", "execution", "agent-interface"],
    "design": ["taste", "standards", "judgment", "voice", "feedback"],
    "sales": ["identity", "relationships", "standards", "voice", "judgment", "direction"],
    "research": ["cognition", "context", "workflow", "standards", "memory"],
    "founder_comms": ["identity", "voice", "judgment", "relationships", "standards"],
    "planning": ["direction", "execution", "environment", "judgment", "workflow"],
    "general": ["core", "context", "judgment", "standards"],
}


def classify_task(task: str) -> str:
    t = f" {(task or '').lower()} "
    if any(w in t for w in ("write", "post", "thread", "essay", "caption", "copy")):
        return "writing"
    if any(w in t for w in ("build", "product", "feature", "spec", "launch")):
        return "product"
    if any(w in t for w in ("strategy", "decide", "pivot", "should i", "positioning")):
        return "strategy"
    if any(w in t for w in ("code", "bug", "test", "refactor", "api", "server")):
        return "code"
    if any(w in t for w in ("design", "ui", "ux", "visual")):
        return "design"
    if any(w in t for w in ("sales", "dm", "offer", "prospect", "customer")):
        return "sales"
    if any(w in t for w in ("research", "synthesize", "compare", "analyze")):
        return "research"
    if any(w in t for w in ("founder", "investor", "public", "announcement")):
        return "founder_comms"
    if any(w in t for w in ("plan", "roadmap", "next actions", "sprint")):
        return "planning"
    return "general"


def select_subbrains(task_type: str) -> list[str]:
    return TASK_ROUTES.get(task_type, TASK_ROUTES["general"])


def build_context_packet(task: str, project: str | None = None, agent: str | None = None,
                         state_root: Path = store.STATE_ROOT) -> dict:
    task_type = classify_task(task)
    selected = select_subbrains(task_type)
    query = task + " " + " ".join(selected)
    relevant = [
        m for m in memory.search_memories(query, project=project, limit=30, state_root=state_root)
        if (m.get("target_brain") in selected or m.get("type") in {"standard", "judgment_signal", "preference", "rejection"})
    ][:12]
    standards = [m for m in relevant if m.get("type") == "standard" or m.get("target_brain") == "standards"]
    rejected = [m for m in relevant if m.get("type") in {"rejection"} or "never" in (m.get("text") or "").lower()]
    workflow = [m for m in relevant if m.get("type") == "workflow" or m.get("target_brain") == "workflow"]
    packet = {
        "id": store.new_id("ctx"),
        "task": task,
        "task_type": task_type,
        "project": project or "default",
        "agent": agent or "unknown",
        "profile_summary": memory.compact_profile(project, state_root),
        "selected_sub_brains": selected,
        "relevant_memories": relevant,
        "standards": standards[:5],
        "rejected_patterns": rejected[:5],
        "workflow_rules": workflow[:5],
        "judgment_contract": {
            "before_work": "recall the selected sub-brains and relevant memories",
            "after_work": "review output against standards, judgment, rejected patterns, and recent feedback",
            "on_feedback": "capture the correction as an event and let Catalyst update memory",
        },
        "warnings": ["no relevant memories yet; use low confidence"] if not relevant else [],
        "source_node_ids": [m["id"] for m in relevant],
        "created_at": store.now_iso(),
    }
    store.append_jsonl("logs/recall.jsonl", packet, state_root)
    return packet

