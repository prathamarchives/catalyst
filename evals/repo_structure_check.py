from pathlib import Path

REQUIRED_FILES = [
    "README.md", "AGENTS.md", "REPO-USE-PROMPT.md", "INSTALL.md", "SETUP-PROMPT.md", "EVAL_REPORT.md", "LICENSE", ".gitignore",
    "prompts/00-start-here.md", "prompts/01-source-audit.md", "prompts/02-interview-user.md", "prompts/03-extract-catalyst-brain.md", "prompts/04-build-catalyst-brain.md", "prompts/05-write-agent-skill.md", "prompts/06-task-time-evaluation.md", "prompts/07-update-from-feedback.md", "prompts/08-install-and-run.md", "prompts/09-distill-and-decay-memory.md",
    "templates/catalyst-brain/README.md", "templates/catalyst-brain/identity.md", "templates/catalyst-brain/context.md", "templates/catalyst-brain/goals.md", "templates/catalyst-brain/constraints.md", "templates/catalyst-brain/standards.md", "templates/catalyst-brain/judgment.md", "templates/catalyst-brain/taste.md", "templates/catalyst-brain/voice.md", "templates/catalyst-brain/anti-slop.md", "templates/catalyst-brain/references.md", "templates/catalyst-brain/rejected-examples.md", "templates/catalyst-brain/decision-rules.md", "templates/catalyst-brain/task-patterns.md", "templates/catalyst-brain/feedback-memory.md", "templates/catalyst-brain/lexicon.md", "templates/catalyst-brain/open-questions.md",
    "templates/skills/catalyst-skill.md", "templates/skills/use-catalyst-brain.md", "templates/skills/update-catalyst-brain.md", "templates/skills/review-against-standards.md", "templates/skills/extract-feedback.md", "templates/skills/task-routing.md", "templates/skills/distill-memory.md",
    "templates/workflows/start-task.md", "templates/workflows/produce-output.md", "templates/workflows/review-output.md", "templates/workflows/update-after-feedback.md", "templates/workflows/weekly-distillation.md",
    "templates/evals/output-review.md", "templates/evals/standards-check.md", "templates/evals/identity-alignment.md", "templates/evals/judgment-check.md", "templates/evals/feedback-capture.md", "templates/evals/improvement-log.md",
    "examples/catalyst-loop/README.md", "examples/catalyst-loop/task-time-evaluation.md", "docs/catalyst-brain.md", "docs/privacy.md", "docs/roadmap.md", "docs/eval-loop.md", "docs/memory-lifecycle.md", "docs/install-vs-use.md", "docs/permission-model.md", "tools/discover_sessions.py",
]

def run(root: Path) -> list:
    failures = []
    for rel in REQUIRED_FILES:
        p = root / rel
        if not p.is_file():
            failures.append(f"missing required file: {rel}")
        elif p.suffix == ".md" and p.stat().st_size < 120:
            failures.append(f"{rel} is too thin")
    outputs = root / "outputs"
    if not outputs.is_dir():
        failures.append("missing outputs/")
    else:
        extras = [p.name for p in outputs.iterdir() if p.name != ".gitkeep"]
        if extras:
            failures.append("outputs/ must contain only .gitkeep")
    return failures

if __name__ == "__main__":
    import sys
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems: print("FAIL repo_structure_check:", p)
    if not problems: print("PASS repo_structure_check")
    sys.exit(1 if problems else 0)
