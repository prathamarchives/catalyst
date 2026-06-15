from pathlib import Path

REQUIREMENTS = [
    ("role", ["## role"]),
    ("Catalyst Brain", ["catalyst brain"]),
    ("identity", ["identity"]),
    ("standards", ["standards"]),
    ("judgment", ["judgment"]),
    ("source discovery", ["discover where"]),
    ("permission", ["authorization", "approve"]),
    ("interview", ["interview"]),
    ("extraction", ["## extraction"]),
    ("output path", ["outputs/<name>/"]),
    ("skills", ["quick mode", "full mode"]),
    ("task-time evaluation", ["task-time evaluation"]),
    ("feedback memory", ["feedback-memory", "feedback memory"]),
    ("privacy", ["## privacy"]),
    ("quality checklist", ["quality checklist"]),
]

def run(root: Path) -> list:
    p = root / "AGENTS.md"
    if not p.is_file(): return ["AGENTS.md is missing"]
    text = p.read_text(encoding="utf-8").lower()
    failures = []
    for name, markers in REQUIREMENTS:
        if not any(m in text for m in markers):
            failures.append(f"AGENTS.md missing required item: {name}")
    return failures

if __name__ == "__main__":
    import sys
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems: print("FAIL protocol_completeness_check:", p)
    if not problems: print("PASS protocol_completeness_check")
    sys.exit(1 if problems else 0)
