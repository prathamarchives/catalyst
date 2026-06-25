"""quality.py — deterministic brain self-audit + distill flag.

Flags placeholder/thin/stale/duplicate sections and scores readiness so the brain
gets sharper, not just longer. No model call.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from . import paths, registry

THIN_CHARS = 200
STALE_DAYS = 120
DISTILL_AT = 10  # feedback-memory entries before recommending a distill pass


def _rule_texts(sec: dict) -> list:
    body = (sec.get("sections", {}).get("evidence / rules", "") + "\n" +
            sec.get("sections", {}).get("seeded from onboarding", ""))
    return [l.split("rule:", 1)[1].strip().lower() for l in body.splitlines() if "rule:" in l]


def audit_brain(name: str, outputs_root: Path = paths.OUTPUTS) -> dict:
    val = registry.validate_brain(name, outputs_root)
    if not val.get("present") and val.get("error"):
        return {"error": val["error"], "ready_score": 0.0}
    flags: dict = {}
    filled = 0
    today = date.today()
    for f in paths.BRAIN_FILE_ORDER:
        if f == "README.md":
            continue
        sec = registry.load_section(name, f, outputs_root)
        issues = []
        if not sec.get("exists"):
            issues.append("missing")
        elif sec.get("empty"):
            issues.append("placeholder (unfilled template)")
        else:
            filled += 1
            content_low = sec.get("content", "").lower()
            rules_body = sec.get("sections", {}).get("evidence / rules", "").strip()
            if len(rules_body) < THIN_CHARS and "seeded from onboarding" not in content_low:
                issues.append("thin (few/short rules)")
            for m in re.findall(r"20\d\d-\d\d-\d\d", sec.get("content", "")):
                try:
                    if (today - datetime.strptime(m, "%Y-%m-%d").date()).days > STALE_DAYS:
                        issues.append(f"stale evidence ({m})")
                        break
                except ValueError:
                    pass
            rules = _rule_texts(sec)
            if any(r and rules.count(r) > 1 for r in rules):
                issues.append("duplicate rules")
        if issues:
            flags[f] = issues
    total = len([f for f in paths.BRAIN_FILE_ORDER if f != "README.md"])
    ready = round(filled / total, 2) if total else 0.0

    distill = None
    bd = paths.brain_dir(name, outputs_root)
    if bd:
        fm = bd / "feedback-memory.md"
        if fm.is_file():
            text = fm.read_text(encoding="utf-8")
            n = text.count("change_type:") + text.lower().count("## feedback")
            if n >= DISTILL_AT:
                distill = f"feedback-memory has ~{n} entries; run the weekly-distillation workflow to compress into rules"

    if ready >= 0.8 and not flags:
        summary = "brain is solid"
    elif ready < 0.4:
        summary = "brain is mostly unfilled - run extraction first"
    else:
        summary = f"{len(flags)} section(s) need tightening"
    return {"name": name, "ready_score": ready, "filled": filled, "total": total,
            "flags": flags, "distill_recommendation": distill, "summary": summary}
