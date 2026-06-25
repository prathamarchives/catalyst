"""evaluator.py — deterministic local review of an output against the brain.

No model call required. `provider` is an adapter boundary for future AI-assisted
evaluation; unused by default and never presented as live when absent.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import paths, registry, router

BUILTIN_SLOP = [
    "in today's fast-paced world", "unlock", "unleash", "elevate", "game-changer", "game changer",
    "seamless", "synergy", "dive in", "in conclusion", "it's important to note", "furthermore",
    "moreover", "delve", "tapestry", "navigate the landscape", "at the end of the day", "supercharge", "revolutionary",
]


def _bad_terms(name: str, files: set, outputs_root: Path) -> list:
    terms = []
    for f in ("anti-slop.md", "rejected-examples.md"):
        if f not in files:
            continue
        sec = registry.load_section(name, f, outputs_root)
        if not sec.get("exists") or sec.get("empty"):
            continue
        body = (sec.get("sections", {}).get("evidence / rules", "") + "\n" +
                sec.get("sections", {}).get("seeded from onboarding", ""))
        for line in body.splitlines():
            m = re.search(r"rule:\s*(.+)", line)
            if m:
                terms.append(m.group(1).strip().lower())
    return terms


def evaluate_output(name: str, task: str, output: str, mode: str = "auto",
                    outputs_root: Path = paths.OUTPUTS, provider=None) -> dict:
    route = router.route_task(name, task, outputs_root)
    files = set(route["files_to_load"])
    out = (output or "").strip()
    out_low = out.lower()
    issues, revision, questions, candidates = [], [], [], []

    slop_hits = [s for s in BUILTIN_SLOP if s in out_low]
    bad_hits = [b for b in _bad_terms(name, files, outputs_root) if b and len(b) > 3 and b in out_low]
    if slop_hits:
        issues.append(f"slop phrases present: {', '.join(slop_hits[:5])}")
        revision.append("remove generic/AI-tell phrases; rewrite plain and specific")
    if bad_hits:
        issues.append(f"matches rejected patterns: {', '.join(bad_hits[:5])}")
        revision.append("avoid the patterns in anti-slop.md / rejected-examples.md")

    def present(f):
        sec = registry.load_section(name, f, outputs_root)
        return bool(sec.get("exists") and not sec.get("empty"))

    def clamp(n):
        return max(0, min(5, n))

    missing_or_unfilled = list(route["missing_files"])
    blocked_by_brain = bool(missing_or_unfilled)
    if blocked_by_brain:
        issues.append("evaluation blocked/limited because the routed Catalyst Brain files are missing or still template placeholders")
        revision.append("build or fill the Catalyst Brain before treating this as an alignment verdict")
        candidates.append("run source discovery, approved scan, extraction, and brain build first")

    scores = {
        "identity_alignment": clamp((4 if present("identity.md") and out else 1 if present("identity.md") else 0) - (0 if out else 1)),
        "standards_match": clamp(4 if present("standards.md") else 0),
        "judgment_match": clamp(4 if present("judgment.md") else 0),
        "taste_match": clamp((4 if present("taste.md") else 1) - len(slop_hits) - len(bad_hits)),
        "anti_slop": clamp(5 - len(slop_hits) - len(bad_hits)),
    }
    if not out:
        questions.append("no output provided to evaluate; produce a draft first")
    if missing_or_unfilled:
        questions.append(f"routed files missing/unfilled: {', '.join(missing_or_unfilled)}")
        candidates.append("fill the missing/placeholder brain files routed for this task")
    if not present("standards.md"):
        questions.append("standards.md has no extracted bar — what does 'good' look like here?")

    avg = sum(scores.values()) / len(scores)
    if not out or blocked_by_brain:
        verdict = "ask"
    elif avg >= 4 and not slop_hits and not bad_hits:
        verdict = "ship"
    elif avg < 3:
        verdict = "reject"
    else:
        verdict = "revise"
    if verdict in ("revise", "reject") and not revision:
        revision.append("tighten against standards.md and judgment.md before shipping")

    return {"task_type": route["task_type"], "files_loaded": sorted(files), "verdict": verdict, "scores": scores,
            "issues": issues, "revision_instructions": revision, "missing_context_questions": questions,
            "brain_update_candidates": candidates,
            "note": "deterministic local evaluation (no model call); pass a BYOK provider to enrich — not enabled by default."}
