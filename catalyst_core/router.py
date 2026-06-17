"""router.py — judgment-aware task classification + retrieval routing.

Not vector search. Classifies a task into a job type and returns the minimal
relevant brain-file bundle with reasons, missing files, and warnings.
"""
from __future__ import annotations

from pathlib import Path

from . import paths, registry

CORE_BUNDLE = [f for f in paths.BRAIN_FILE_ORDER if f != "README.md"]

JOB_TYPES = {
    "writing/content": ["identity.md", "context.md", "standards.md", "judgment.md", "taste.md", "voice.md", "anti-slop.md", "rejected-examples.md", "task-patterns.md"],
    "reply/dm": ["identity.md", "judgment.md", "taste.md", "voice.md", "anti-slop.md", "decision-rules.md"],
    "strategy/decision": ["goals.md", "constraints.md", "standards.md", "judgment.md", "decision-rules.md", "feedback-memory.md"],
    "product/build": ["goals.md", "constraints.md", "standards.md", "judgment.md", "task-patterns.md", "references.md"],
    "research/synthesis": ["goals.md", "context.md", "standards.md", "judgment.md", "taste.md", "references.md", "anti-slop.md"],
    "design/taste": ["identity.md", "standards.md", "judgment.md", "taste.md", "anti-slop.md", "references.md", "rejected-examples.md"],
    "sales/offer": ["identity.md", "goals.md", "standards.md", "judgment.md", "voice.md", "decision-rules.md", "rejected-examples.md"],
    "code/review": ["standards.md", "judgment.md", "constraints.md", "decision-rules.md", "task-patterns.md", "references.md"],
    "life/current-context": ["identity.md", "context.md", "goals.md", "constraints.md", "decision-rules.md"],
    "unknown/high-stakes": list(CORE_BUNDLE),
}

KEYWORDS = {
    "reply/dm": ["dm", "reply", "respond", "responding", "message", "inbox", "comment", "outreach", "cold message"],
    "writing/content": ["write", "post", "thread", "article", "caption", "tweet", "blog", "newsletter", "copy", "draft", "headline"],
    "strategy/decision": ["should i", "decide", "decision", "strategy", "choose", "prioritize", "pivot", "worth it", "which option"],
    "product/build": ["build", "implement", "feature", "ship", "product", "spec", "prototype", "endpoint", "module", "scaffold"],
    "research/synthesis": ["research", "summarize", "synthesize", "analyze", "compare", "findings", "study", "investigate", "report on"],
    "design/taste": ["design", "ui", "ux", "layout", "visual", "aesthetic", "landing page", "mockup", "interface", "wireframe"],
    "sales/offer": ["offer", "pitch", "sell", "pricing", "price", "proposal", "client", "sales", "close the", "package"],
    "code/review": ["review code", "code review", "refactor", "bug", "pull request", " pr ", "debug", "lint", "stack trace"],
    "life/current-context": ["my day", "schedule", "personal", "my life", "routine", "plan my", "habit", "current situation"],
}

HIGH_STAKES = ["investor", "legal", "lawyer", "public launch", "press", "high-stakes",
               "high stakes", "irreversible", "contract", "lawsuit", "acquisition"]

WHY = {
    "identity.md": "who the agent represents; keeps output in character",
    "context.md": "current situation; keeps output relevant to now",
    "goals.md": "desired outcomes; keeps work pointed at what matters",
    "constraints.md": "hard limits the output must not cross",
    "standards.md": "the quality bar the output must clear",
    "judgment.md": "ship/revise/reject logic for the verdict",
    "taste.md": "aesthetic/style preferences to match",
    "voice.md": "how it should sound",
    "anti-slop.md": "weak patterns to avoid",
    "rejected-examples.md": "killed outputs to never repeat",
    "decision-rules.md": "rules for choosing between options",
    "task-patterns.md": "the recurring pattern for this task",
    "references.md": "what to learn from / not copy",
    "feedback-memory.md": "durable corrections from past tasks",
    "lexicon.md": "the user's words and meanings",
    "open-questions.md": "known unknowns to flag",
}


def classify_task(task: str) -> tuple:
    t = f" {(task or '').lower()} "
    if any(h in t for h in HIGH_STAKES):
        return ("unknown/high-stakes", 0.5)
    scores = {jt: sum(1 for w in words if w in t) for jt, words in KEYWORDS.items()}
    best = max(scores, key=lambda k: scores[k])
    top = scores[best]
    if top == 0:
        return ("unknown/high-stakes", 0.2)
    ordered = sorted(scores.values(), reverse=True)
    margin = top - (ordered[1] if len(ordered) > 1 else 0)
    return (best, round(min(1.0, 0.5 + 0.15 * top + 0.1 * margin), 2))


def route_task(name: str, task: str, outputs_root: Path = paths.OUTPUTS) -> dict:
    bd = paths.brain_dir(name, outputs_root)
    task_type, confidence = classify_task(task)
    bundle = JOB_TYPES.get(task_type, JOB_TYPES["unknown/high-stakes"])
    files_to_load, missing, why, warnings = [], [], {}, []
    for f in bundle:
        sec = registry.load_section(name, f, outputs_root) if bd else {"exists": False, "empty": True}
        if sec.get("exists") and not sec.get("empty"):
            files_to_load.append(f)
            why[f] = WHY.get(f, "relevant brain file")
        elif sec.get("exists"):
            files_to_load.append(f)
            why[f] = WHY.get(f, "relevant brain file") + " (present but unfilled)"
            missing.append(f + " (placeholder)")
        else:
            missing.append(f)
    if bd is None:
        warnings.append(f"no brain found for '{name}'")
    if task_type == "unknown/high-stakes":
        warnings.append("high-stakes or unclassified; loaded the expanded bundle, use full mode")
    if confidence < 0.5:
        warnings.append(f"low confidence ({confidence}); verify the task type")
    if missing:
        warnings.append(f"{len(missing)} routed file(s) missing or unfilled")
    return {"task_type": task_type, "confidence": confidence, "files_to_load": files_to_load,
            "why_each_file": why, "missing_files": missing, "warnings": warnings}
