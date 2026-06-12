"""Eval: required repo structure exists and is non-hollow."""
from pathlib import Path

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "REPO-USE-PROMPT.md",
    "EVAL_REPORT.md",
    "LICENSE",
    ".gitignore",
    "prompts/00-start-here.md",
    "prompts/01-source-audit.md",
    "prompts/02-interview-user.md",
    "prompts/03-extract-creative-identity.md",
    "prompts/04-build-creative-brain.md",
    "prompts/05-write-agent-skill.md",
    "prompts/06-run-before-after-proof.md",
    "prompts/07-update-from-feedback.md",
    "templates/creative-brain/README.md",
    "templates/creative-brain/identity.md",
    "templates/creative-brain/context.md",
    "templates/creative-brain/voice.md",
    "templates/creative-brain/taste.md",
    "templates/creative-brain/judgment.md",
    "templates/creative-brain/anti-slop.md",
    "templates/creative-brain/references.md",
    "templates/creative-brain/rejected-examples.md",
    "templates/creative-brain/feedback-memory.md",
    "templates/creative-brain/lexicon.md",
    "templates/skills/creative-identity-skill.md",
    "templates/workflows/use-creative-brain.md",
    "templates/workflows/update-from-feedback.md",
    "templates/workflows/review-output.md",
    "examples/pratham-mini/README.md",
    "examples/pratham-mini/before-after.md",
    "examples/pratham-mini/creative-brain/identity.md",
    "examples/pratham-mini/creative-brain/context.md",
    "examples/pratham-mini/creative-brain/voice.md",
    "examples/pratham-mini/creative-brain/taste.md",
    "examples/pratham-mini/creative-brain/judgment.md",
    "examples/pratham-mini/creative-brain/anti-slop.md",
    "examples/pratham-mini/creative-brain/references.md",
    "examples/pratham-mini/creative-brain/rejected-examples.md",
    "examples/pratham-mini/creative-brain/feedback-memory.md",
    "examples/pratham-mini/creative-brain/lexicon.md",
    "examples/pratham-mini/skills/creative-identity-skill.md",
    "examples/pratham-mini/workflows/use-creative-brain.md",
    "examples/pratham-mini/workflows/update-from-feedback.md",
    "examples/pratham-mini/workflows/review-output.md",
    "outputs/.gitkeep",
    "docs/philosophy.md",
    "docs/privacy.md",
    "docs/roadmap.md",
    "docs/eval-loop.md",
    "evals/run_all.py",
    "evals/repo_structure_check.py",
    "evals/content_slop_check.py",
    "evals/protocol_completeness_check.py",
    "evals/privacy_check.py",
    "evals/example_proof_check.py",
    "evals/agent_runnability_static_check.py",
    "evals/vision_fit_check.py",
    "evals/rubrics/agent_runnability.md",
    "evals/rubrics/taste_quality.md",
    "evals/rubrics/vision_fit.md",
    "tools/discover_sessions.py",
]

# Directories whose markdown files must contain real content, not stubs.
MIN_CONTENT_BYTES = 200
NON_EMPTY_DIRS = ["prompts", "templates"]


def run(root: Path) -> list:
    failures = []

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            failures.append("missing required file: %s" % rel)

    outputs = root / "outputs"
    if not outputs.is_dir():
        failures.append("missing required directory: outputs/")
    else:
        extras = [p.name for p in outputs.iterdir() if p.name != ".gitkeep"]
        if extras:
            failures.append(
                "outputs/ must contain only .gitkeep, found: %s" % ", ".join(sorted(extras))
            )

    if not (root / "examples" / "pratham-mini").is_dir():
        failures.append("missing required directory: examples/pratham-mini/")

    for dirname in NON_EMPTY_DIRS:
        base = root / dirname
        if not base.is_dir():
            continue  # already reported as missing files above
        for md in sorted(base.rglob("*.md")):
            size = md.stat().st_size
            if size < MIN_CONTENT_BYTES:
                failures.append(
                    "%s is too thin (%d bytes < %d): templates and prompts must be useful, not stubs"
                    % (md.relative_to(root).as_posix(), size, MIN_CONTENT_BYTES)
                )

    return failures


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL repo_structure_check: %s" % p)
    if not problems:
        print("PASS repo_structure_check")
    sys.exit(1 if problems else 0)
