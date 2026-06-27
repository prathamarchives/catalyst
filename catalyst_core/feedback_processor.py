"""Structured feedback classification and proposal creation."""
from __future__ import annotations

from pathlib import Path

from . import capture, proposal_engine, store

FEEDBACK_TARGETS = {
    "style_voice_correction": ["voice", "taste"],
    "taste_judgment_correction": ["judgment", "taste"],
    "rejected_pattern": ["judgment", "rejected-examples", "anti-slop"],
    "approved_pattern": ["judgment", "references", "taste"],
    "factual_context_update": ["context", "identity"],
    "workflow_task_pattern_update": ["task-patterns", "feedback-memory"],
    "decision_rule": ["decision-rules", "judgment"],
    "anti_slop_quality_rule": ["standards", "anti-slop"],
    "unclear_feedback": ["open-questions", "feedback-memory"],
}


def classify_feedback(feedback: str, output: str = "", task: str = "") -> dict:
    low = f" {feedback or ''} {output or ''} {task or ''} ".lower()
    if any(w in low for w in ("never", "reject", "wrong", "don't", "do not", "stop", "cringe")):
        ftype = "rejected_pattern"
    elif any(w in low for w in ("approved", "ship this", "good", "keep this", "this works")):
        ftype = "approved_pattern"
    elif any(w in low for w in ("tone", "voice", "sound", "phrasing", "too formal", "too casual")):
        ftype = "style_voice_correction"
    elif any(w in low for w in ("fact", "actually", "context", "remember that", "constraint")):
        ftype = "factual_context_update"
    elif any(w in low for w in ("workflow", "process", "always", "step", "before you")):
        ftype = "workflow_task_pattern_update"
    elif any(w in low for w in ("decide", "decision", "if ", "when ", "should")):
        ftype = "decision_rule"
    elif any(w in low for w in ("generic", "slop", "quality", "specific", "proof", "concrete")):
        ftype = "anti_slop_quality_rule"
    else:
        ftype = "unclear_feedback"
    confidence = 0.78 if ftype != "unclear_feedback" else 0.35
    return {
        "feedback_type": ftype,
        "target_sections": FEEDBACK_TARGETS[ftype],
        "rule_candidate": (feedback or "").strip(),
        "evidence": (feedback or output or task or "").strip(),
        "confidence": confidence,
    }


def capture_feedback_structured(task: str, output: str, feedback: str, project: str = "default",
                                source: str = "user", state_root: Path = store.STATE_ROOT) -> dict:
    if not (feedback or "").strip():
        return {"error": "feedback is required"}
    classification = classify_feedback(feedback, output, task)
    event_type = "approval" if classification["feedback_type"] == "approved_pattern" else "correction"
    captured = capture.capture_event({
        "type": event_type,
        "project": project,
        "agent": source,
        "task": task,
        "output": output,
        "user_feedback": feedback,
        "outcome": classification["feedback_type"],
        "metadata": {"feedback_type": classification["feedback_type"], "source": source},
    }, state_root=state_root)
    proposal_ids = []
    for section in classification["target_sections"][:3]:
        proposal = proposal_engine.create_brain_update(
            project=project,
            target_section=f"{section}.md" if section.endswith("-examples") else section,
            proposed_change=classification["rule_candidate"],
            reason=f"structured feedback classified as {classification['feedback_type']}",
            source_event_id=captured.get("event_id"),
            source_memory_id=(captured.get("memory_ids") or [""])[0] or None,
            confidence=classification["confidence"],
            state_root=state_root,
        )
        proposal_ids.append(proposal.get("id"))
    return {
        "ok": True,
        **classification,
        "event_id": captured.get("event_id"),
        "signal_ids": captured.get("signal_ids", []),
        "memory_ids": captured.get("memory_ids", []),
        "proposal_ids": [p for p in proposal_ids if p],
        "capture": captured,
    }

