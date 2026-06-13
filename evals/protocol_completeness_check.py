"""Eval: AGENTS.md contains every required section of the protocol.

Each requirement is satisfied if ANY of its marker phrases appears in
AGENTS.md (case-insensitive). Failures name the exact missing item.
"""
from pathlib import Path

REQUIREMENTS = [
    ("role", ["## role", "role of the agent"]),
    ("do not write content first", ["do not write content first"]),
    ("source audit", ["source audit"]),
    ("interview", ["interview"]),
    ("extraction", ["## extraction", "extraction rules", "extract taste"]),
    ("evidence / quotes", ["evidence", "quote"]),
    ("creative brain", ["creative brain"]),
    ("output path (outputs/<name>/)", ["outputs/<user-or-project>/", "outputs/<name>/"]),
    ("never overwrite templates", ["never overwrite templates", "do not overwrite anything under `templates/`"]),
    ("skill writing", ["catalyst-skill", "write a reusable skill"]),
    ("before/after proof", ["before/after proof", "before/after"]),
    ("feedback memory", ["feedback-memory", "feedback memory"]),
    ("privacy", ["## privacy", "privacy rules"]),
    ("quality checklist", ["quality checklist"]),
]


def run(root: Path) -> list:
    agents = root / "AGENTS.md"
    if not agents.is_file():
        return ["AGENTS.md is missing"]
    lower = agents.read_text(encoding="utf-8").lower()

    failures = []
    for item, markers in REQUIREMENTS:
        if item == "evidence / quotes":
            # require both words somewhere, not either
            if not ("evidence" in lower and "quote" in lower):
                failures.append("AGENTS.md missing required item: evidence / quotes")
            continue
        if not any(marker in lower for marker in markers):
            failures.append("AGENTS.md missing required item: %s" % item)
    return failures


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL protocol_completeness_check: %s" % p)
    if not problems:
        print("PASS protocol_completeness_check")
    sys.exit(1 if problems else 0)
