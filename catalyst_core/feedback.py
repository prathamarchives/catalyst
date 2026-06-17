"""feedback.py — turn a correction into append-only logs + a review proposal.

Never silently mutates core brain rule files. Appends a marked entry to
feedback-memory.md and improvement-log.md, and writes a dated proposal under
outputs/<name>/proposals/ classified as add | refine | retire.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from . import paths, router


def _classify_change(fb: str) -> str:
    low = (fb or "").lower()
    if any(w in low for w in ("never", "stop", "drop", "remove", "don't", "do not", "retire")):
        return "retire"
    if any(w in low for w in ("more", "less", "tighten", "instead", "rather", "closer", "too ")):
        return "refine"
    return "add"


def _affected_files(name: str, task: str, fb: str, outputs_root: Path) -> list:
    route = router.route_task(name, task, outputs_root)
    base = list(route["files_to_load"]) or ["judgment.md", "standards.md"]
    low = (fb or "").lower()
    extra = []
    if any(w in low for w in ("pitch", "salesy", "polished", "tone", "sound", "human")):
        extra += ["voice.md", "anti-slop.md", "taste.md"]
    if any(w in low for w in ("wrong", "reject", "never", "don't", "do not")):
        extra += ["rejected-examples.md", "judgment.md"]
    seen, ordered = set(), []
    for f in base + extra:
        if f not in seen:
            seen.add(f)
            ordered.append(f)
    return ordered


def capture_feedback(name: str, task: str, output: str, feedback: str,
                     outputs_root: Path = paths.OUTPUTS) -> dict:
    bd = paths.brain_dir(name, outputs_root)
    if bd is None:
        return {"error": f"no brain for '{name}'"}
    fb = (feedback or "").strip()
    if not fb:
        return {"error": "empty feedback"}
    now = datetime.now()
    stamp, day = now.strftime("%Y-%m-%d-%H%M%S"), now.strftime("%Y-%m-%d")
    change_type = _classify_change(fb)
    affected = _affected_files(name, task, fb, outputs_root)
    slug = paths.slug(name)
    written = []

    fm = bd / "feedback-memory.md"
    block = ("\n\n## feedback (via catalyst flow)\n\n"
             f"- date: {day}\n  status: observed\n  change_type: {change_type}\n"
             "  evidence: captured through catalyst_core.feedback.capture_feedback\n"
             f"  task: {task.strip()}\n  rule: {fb}\n")
    fm.write_text((fm.read_text(encoding="utf-8") if fm.is_file() else "# feedback-memory\n") + block, encoding="utf-8")
    written.append(f"outputs/{slug}/catalyst-brain/feedback-memory.md")

    log = bd.parent / "evals" / "improvement-log.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    entry = ("\n\n## entry\n\n```txt\n"
             f"date: {day}\ntask: {task.strip()}\nfiles loaded: {', '.join(affected)}\n"
             f"result: feedback captured ({change_type})\nuser feedback: {fb}\nrule learned: {fb}\n"
             f"files updated: feedback-memory.md (+ proposal {stamp})\n"
             "next-time check: apply this rule before showing similar output\n```\n")
    log.write_text((log.read_text(encoding="utf-8") if log.is_file() else "# improvement-log\n") + entry, encoding="utf-8")
    written.append(f"outputs/{slug}/evals/improvement-log.md")

    prop_dir = bd.parent / "proposals"
    prop_dir.mkdir(parents=True, exist_ok=True)
    pfile = prop_dir / f"{stamp}-feedback-update.md"
    verb = {"add": "add a rule reflecting", "refine": "tighten the existing rule toward",
            "retire": "retire/replace the rule that conflicts with"}[change_type]
    patches = "\n".join(f"- `catalyst-brain/{f}`: {verb} — {fb}" for f in affected)
    pfile.write_text(
        f"# proposed brain update — {stamp}\n\n"
        "Not applied. Review and merge manually or via the update-after-feedback workflow.\n\n"
        f"## feedback summary\n\n{fb}\n\n## task\n\n{task.strip()}\n\n## change type\n\n{change_type}\n\n"
        f"## likely rule learned\n\n{fb}\n\n## affected brain files\n\n{', '.join(affected)}\n\n"
        f"## suggested patches\n\n{patches}\n\n## needs confirmation?\n\nyes\n",
        encoding="utf-8")
    written.append(f"outputs/{slug}/proposals/{stamp}-feedback-update.md")

    return {"ok": True, "change_type": change_type, "affected_files": affected, "written": written,
            "proposal": f"outputs/{slug}/proposals/{stamp}-feedback-update.md", "applied": False}
