from pathlib import Path
ENTRY_FILES = ["README.md", "AGENTS.md", "REPO-USE-PROMPT.md", "prompts/00-start-here.md"]
REQUIREMENTS = [
    ("clear first action", ["first action"]),
    ("discovers source locations first", ["discover where", "discovered locations"]),
    ("asks approval", ["approve", "authorized", "what you may scan"]),
    ("output path", ["outputs/<name>/"]),
    ("small interview rounds", ["small rounds"]),
    ("never overwrite templates", ["never overwrite"]),
    ("write generated skills", ["catalyst-skill"]),
    ("task-time evaluation", ["task-time evaluation"]),
    ("update feedback", ["feedback-memory", "update the system"]),
]

def run(root: Path) -> list:
    corpus = ""
    failures = []
    for rel in ENTRY_FILES:
        p = root / rel
        if not p.is_file(): failures.append(f"missing entry file: {rel}")
        else: corpus += "\n" + p.read_text(encoding="utf-8").lower()
    for req, markers in REQUIREMENTS:
        if not any(m in corpus for m in markers):
            failures.append(f"entry files do not establish: {req}")
    for stale in ["start by asking where my source material lives", "run before/after proof"]:
        if stale in corpus:
            failures.append(f"stale phrase remains: {stale}")
    return failures

if __name__ == "__main__":
    import sys
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems: print("FAIL agent_runnability_static_check:", p)
    if not problems: print("PASS agent_runnability_static_check")
    sys.exit(1 if problems else 0)
