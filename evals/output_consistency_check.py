from pathlib import Path

FILES = ["AGENTS.md", "prompts/04-build-catalyst-brain.md", "README.md"]
OUTPUT_TOKENS = [
    "catalyst-brain", "standards.md", "judgment.md", "decision-rules.md", "task-patterns.md", "feedback-memory.md",
    "use-catalyst-brain", "update-catalyst-brain", "review-against-standards", "extract-feedback", "task-routing", "distill-memory",
    "output-review", "standards-check", "identity-alignment", "judgment-check", "feedback-capture", "improvement-log",
]

def run(root: Path) -> list:
    failures = []
    texts = {}
    for rel in FILES:
        p = root / rel
        if not p.is_file():
            failures.append(f"missing file: {rel}")
        else:
            texts[rel] = p.read_text(encoding="utf-8").lower()
    for token in OUTPUT_TOKENS:
        missing = [rel for rel, text in texts.items() if token not in text]
        if missing:
            failures.append(f"output token '{token}' missing from: {', '.join(missing)}")
    skill = (root / "templates/skills/catalyst-skill.md").read_text(encoding="utf-8").lower()
    for mode in ["quick mode", "full mode"]:
        if mode not in skill:
            failures.append(f"skill template omits {mode}")
    return failures

if __name__ == "__main__":
    import sys
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems: print("FAIL output_consistency_check:", p)
    if not problems: print("PASS output_consistency_check")
    sys.exit(1 if problems else 0)
