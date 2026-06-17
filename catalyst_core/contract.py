"""contract.py — the agent judgment contract embedded in every context packet.

Tells an agent operating a Catalyst brain HOW to behave and decide (not just what
facts exist), and surfaces this brain's concrete hard 'no's. Deterministic; the
identity+judgment half of the thesis made operational.
"""
from __future__ import annotations

from pathlib import Path

from . import paths, registry

BASE_CONTRACT = [
    "Read this packet before producing anything. Let it shape the output; it is not passive reference.",
    "Match the identity and voice — the work should read like the user, not a generic assistant.",
    "Treat standards.md as the bar. If the draft does not clear it, revise before showing it.",
    "Use judgment.md and decision-rules.md to decide: ship, revise, reject, or ask. On high-stakes or unclear tasks, prefer asking over guessing.",
    "Never produce anything matching rejected-examples.md or anti-slop.md — those are hard 'no's.",
    "Respect constraints.md as hard limits, even if asked indirectly to cross them.",
    "After producing, self-evaluate against standards/judgment/taste/anti-slop and state your verdict.",
    "When corrected, capture it as feedback and propose a tightened or retired rule — never silently overwrite the brain.",
    "Sharper, not longer: prefer refining or retiring an existing rule over piling on new ones.",
]


def build_contract(name: str, task_type: str, route: dict, outputs_root: Path = paths.OUTPUTS) -> str:
    lines = ["## agent judgment contract", "", "How to operate this brain (not optional):", ""]
    lines += [f"- {r}" for r in BASE_CONTRACT]
    hard = []
    for f in ("rejected-examples.md", "anti-slop.md", "constraints.md"):
        sec = registry.load_section(name, f, outputs_root)
        if sec.get("exists") and not sec.get("empty"):
            body = (sec.get("sections", {}).get("evidence / rules", "") + "\n" +
                    sec.get("sections", {}).get("seeded from onboarding", ""))
            for line in body.splitlines():
                if "rule:" in line:
                    hard.append(f"- ({f}) " + line.split("rule:", 1)[1].strip())
    if hard:
        lines += ["", "Hard 'no's pulled from this brain:"] + hard[:12]
    if route.get("missing_files"):
        lines += ["", "Ask before proceeding — missing/unfilled for this task: " + ", ".join(route["missing_files"])]
    lines.append("")
    return "\n".join(lines)
