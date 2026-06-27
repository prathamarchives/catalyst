"""Structured local output evaluation against Catalyst brain/runtime state."""
from __future__ import annotations

from pathlib import Path

from . import context_assembler, evaluator, paths, proposal_engine, store
from .models import EvalIssue, EvalResult


DIMENSIONS = [
    "standards_alignment",
    "judgment_alignment",
    "rejected_pattern_risk",
    "taste_voice_fit",
    "task_fit",
    "specificity_proof_concreteness",
    "safety_privacy",
]


def evaluate_output_structured(task: str, output: str, project: str = "default",
                               state_root: Path = store.STATE_ROOT,
                               outputs_root: Path = paths.OUTPUTS) -> dict:
    packet = context_assembler.assemble_context(
        task, project=project, agent="evaluator", state_root=state_root, outputs_root=outputs_root
    )
    old = evaluator.evaluate_output(project, task, output, outputs_root=outputs_root)
    out_low = (output or "").lower()
    issues: list[EvalIssue] = []
    violated = []
    matched = []
    scores = {k: 3.0 for k in DIMENSIONS}
    scores["specificity_proof_concreteness"] = 4.0 if any(ch.isdigit() for ch in output or "") or len((output or "").split()) > 18 else 2.0
    scores["task_fit"] = 4.0 if (task or "").strip() and (output or "").strip() else 1.0
    scores["safety_privacy"] = 5.0
    for pattern in packet.get("rejected_patterns", []):
        text = (pattern.get("pattern") or pattern.get("text") or "").lower()
        if text and len(text) > 6 and text in out_low:
            violated.append(text)
    for rule in packet.get("judgment_rules", []) + packet.get("standards", []):
        text = (rule.get("text") or "").lower()
        if text and any(tok in out_low for tok in text.split()[:4]):
            matched.append(rule.get("text") or "")
    for issue in old.get("issues", []):
        issues.append(EvalIssue(id=store.new_id("issue"), severity="warn", dimension="legacy", message=issue))
    if violated:
        scores["rejected_pattern_risk"] = 0.0
        issues.append(EvalIssue(id=store.new_id("issue"), severity="block", dimension="rejected_pattern_risk",
                                message="output matches rejected patterns", evidence=", ".join(violated[:3]),
                                suggested_fix="remove or rewrite the rejected pattern before showing the user"))
    else:
        scores["rejected_pattern_risk"] = 5.0
    if packet.get("confidence", 0) < 0.45:
        issues.append(EvalIssue(id=store.new_id("issue"), severity="info", dimension="confidence",
                                message="brain context is thin; evaluation confidence is low",
                                suggested_fix="capture more feedback or build the Catalyst Brain before treating this as final"))
    scores["standards_alignment"] = max(0.0, float(old.get("scores", {}).get("standards_match", 0)))
    scores["judgment_alignment"] = max(0.0, float(old.get("scores", {}).get("judgment_match", 0)))
    scores["taste_voice_fit"] = max(0.0, float(old.get("scores", {}).get("taste_match", 0)))
    verdict = old.get("verdict", "ask")
    proposal_ids = []
    if verdict in {"reject", "revise"} and (output or "").strip():
        prop = proposal_engine.create_brain_update(
            project,
            "feedback-memory",
            f"Review failure on task '{task}': {', '.join(old.get('issues', [])[:3]) or 'needs sharper standard'}",
            "structured evaluator suggested feedback capture",
            confidence=0.45,
            state_root=state_root,
        )
        proposal_ids.append(prop.get("id", ""))
    result = EvalResult(
        verdict=verdict,
        scores=scores,
        issues=issues,
        matched_rules=matched[:10],
        violated_patterns=violated[:10],
        suggested_feedback=old.get("revision_instructions", []),
        proposal_ids=[p for p in proposal_ids if p],
        confidence=packet.get("confidence", 0.0),
        metadata={"task_type": packet.get("task_type"), "sections_loaded": packet.get("sections_loaded", [])},
    )
    data = result.model_dump()
    data["legacy"] = old
    return data
