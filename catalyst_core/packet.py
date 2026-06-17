"""packet.py — build a compact markdown context packet before an agent works.

Includes the agent judgment contract and exact source paths. quick/full/auto.
"""
from __future__ import annotations

from pathlib import Path

from . import paths, registry, router, contract

PACKET_SECTIONS = [
    ("identity/context summary", ["identity.md", "context.md", "goals.md"]),
    ("standards to apply", ["standards.md"]),
    ("judgment/rejection rules", ["judgment.md", "decision-rules.md", "rejected-examples.md"]),
    ("taste/voice/anti-slop", ["taste.md", "voice.md", "anti-slop.md"]),
    ("constraints", ["constraints.md"]),
]
REQUIRED_EVAL = ("Run catalyst_core.evaluator.evaluate_output (or `catalyst evaluate`): score "
                 "identity/standards/judgment/taste/anti-slop, decide ship | revise | reject | ask, "
                 "then capture any correction with `catalyst feedback`.")


def _body(sec: dict) -> str:
    if not sec.get("exists"):
        return "_(missing — not in this brain)_"
    if sec.get("empty"):
        return "_(present but unfilled — still the template placeholder)_"
    p = sec.get("sections", {})
    body = p.get("seeded from onboarding") or p.get("evidence / rules") or p.get("how to apply") or ""
    return body.strip() or "_(no extracted rules yet)_"


def build_context_packet(name: str, task: str, mode: str = "auto", outputs_root: Path = paths.OUTPUTS) -> str:
    route = router.route_task(name, task, outputs_root)
    task_type = route["task_type"]
    if mode == "auto":
        mode = "full" if (task_type == "unknown/high-stakes" or route["confidence"] < 0.5) else "quick"
    load = set(route["files_to_load"]) | {
        m.replace(" (placeholder)", "") for m in route["missing_files"] if m.endswith("(placeholder)")
    }
    if mode == "full":
        load = set(router.JOB_TYPES["unknown/high-stakes"])
    lines = ["# Catalyst Context Packet", "", f"brain: {name}", f"task: {task}",
             f"task_type: {task_type} (confidence {route['confidence']}, mode {mode})",
             f"loaded files: {', '.join(sorted(load)) or '(none)'}", ""]
    if route["warnings"]:
        lines += ["> warnings: " + "; ".join(route["warnings"]), ""]
    for label, files in PACKET_SECTIONS:
        lines.append(f"## {label}")
        shown = False
        for f in files:
            if f not in load:
                continue
            shown = True
            sec = registry.load_section(name, f, outputs_root)
            src = sec.get("rel_path") or f"outputs/{paths.slug(name)}/catalyst-brain/{f}"
            lines += [f"### {f}  — source: {src}", _body(sec)]
        if not shown:
            lines.append("_(no files routed for this section in this mode)_")
        lines.append("")
    lines.append(contract.build_contract(name, task_type, route, outputs_root))
    lines += ["## required evaluation after output", REQUIRED_EVAL, ""]
    return "\n".join(lines)
