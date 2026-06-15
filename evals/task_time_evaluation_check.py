from pathlib import Path

INSPECT = ["AGENTS.md", "README.md", "prompts/06-task-time-evaluation.md", "templates/evals/output-review.md", "templates/evals/improvement-log.md"]
REQUIREMENTS = ["classify", "load relevant", "standards", "judgment", "feedback", "update", "improvement-log"]
BANNED_CENTRAL = ["before/after proof", "same model. different brain", "write like you"]

def run(root: Path) -> list:
    failures = []
    corpus = ""
    for rel in INSPECT:
        p = root / rel
        if not p.is_file(): failures.append(f"missing file: {rel}")
        else: corpus += "\n" + p.read_text(encoding="utf-8").lower()
    for req in REQUIREMENTS:
        if req not in corpus:
            failures.append(f"task-time loop missing: {req}")
    public = "\n".join((root / rel).read_text(encoding="utf-8").lower() for rel in ["README.md", "AGENTS.md"] if (root / rel).is_file())
    for phrase in BANNED_CENTRAL:
        if phrase in public:
            failures.append(f"stale central positioning remains: {phrase}")
    return failures

if __name__ == "__main__":
    import sys
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems: print("FAIL task_time_evaluation_check:", p)
    if not problems: print("PASS task_time_evaluation_check")
    sys.exit(1 if problems else 0)
