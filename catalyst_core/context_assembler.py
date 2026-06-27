"""Task routing + compact context assembly for agents."""
from __future__ import annotations

from pathlib import Path

from . import brain_manager, paths, recall, retrieval, store


def assemble_context(task: str, project: str = "default", agent: str = "manual",
                     state_root: Path = store.STATE_ROOT,
                     outputs_root: Path = paths.OUTPUTS) -> dict:
    task_type = recall.classify_task(task)
    selected = recall.select_subbrains(task_type)
    profile = brain_manager.load_brain_profile(project, outputs_root)
    validation = brain_manager.validate_brain_profile(profile)
    query = f"{task} {' '.join(selected)}"
    atoms = retrieval.retrieve_memory_atoms(query, project=project, limit=12, state_root=state_root)
    sections = retrieval.retrieve_brain_sections(query, project=project, limit=8, outputs_root=outputs_root)
    standards = [s.model_dump() for s in profile.standards[:8]]
    judgments = [j.model_dump() for j in profile.judgment_rules[:8]]
    rejected = [r.model_dump() for r in profile.rejected_patterns[:8]]
    approved = [a.model_dump() for a in profile.approved_examples[:5]]
    confidence = 0.25
    if atoms:
        confidence += 0.25
    if standards or judgments or rejected:
        confidence += 0.35
    if validation["warnings"]:
        confidence -= 0.15
    confidence = max(0.0, min(1.0, confidence))
    return {
        "task": task,
        "project": project,
        "agent": agent,
        "task_type": task_type,
        "sections_loaded": [s["name"] for s in sections] or [f"{b}/_index" for b in selected],
        "selected_sub_brains": selected,
        "standards": standards,
        "judgment_rules": judgments,
        "rejected_patterns": rejected,
        "approved_examples": approved,
        "memory_atoms": atoms,
        "instructions_for_agent": (
            "Use the selected standards, judgment rules, rejected patterns, and memory atoms. "
            "Review important output before showing it. Capture user approval, rejection, or correction after the turn."
        ),
        "budget_notes": "Compact packet: relevant sections and up to 12 memory atoms; do not load the whole brain unless confidence is low.",
        "confidence": round(confidence, 2),
        "reasons": [
            f"task classified as {task_type}",
            "standards/judgment/rejections are prioritized over generic memory",
            "recent feedback and rejection memory receive retrieval boost",
        ],
        "warnings": validation["warnings"] + (["low context confidence; ask or build more brain signal"] if confidence < 0.45 else []),
        "created_at": store.now_iso(),
    }
