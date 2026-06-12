"""Eval: a fresh agent can run this repo from its entry files alone.

Static check over README.md, AGENTS.md, REPO-USE-PROMPT.md and
prompts/00-start-here.md: the combined corpus must state the first
action, ask for source material, name the output path, enforce small
interview rounds, protect templates, require the generated skill, the
before/after proof, and the feedback update loop.
"""
from pathlib import Path

ENTRY_FILES = [
    "README.md",
    "AGENTS.md",
    "REPO-USE-PROMPT.md",
    "prompts/00-start-here.md",
]

# (requirement, marker phrases -- ANY must appear in the combined corpus)
CORPUS_REQUIREMENTS = [
    ("clear first action", ["first action"]),
    ("asks user for source material", ["where does your source material live", "where your source material", "where my source material"]),
    ("tells agent where to create outputs", ["outputs/<name>/", "outputs/<user-or-project>/"]),
    ("small interview rounds", ["small rounds"]),
    ("never overwrite templates", ["never overwrite templates", "never overwrite anything in `templates/`", "never edit these masters"]),
    ("write the generated skill", ["creative-identity-skill"]),
    ("run before/after proof", ["before/after proof", "before/after"]),
    ("update from feedback", ["update-from-feedback", "update feedback-memory", "update the system"]),
]

# The first-run file specifically must lead with the first action.
START_FILE_REQUIREMENTS = [
    ("first action stated in prompts/00-start-here.md", ["first action"]),
    ("00-start-here asks for sources before anything", ["where does your source material live"]),
]


def run(root: Path) -> list:
    failures = []
    corpus_parts = []
    for rel in ENTRY_FILES:
        path = root / rel
        if not path.is_file():
            failures.append("missing entry file: %s" % rel)
            continue
        corpus_parts.append(path.read_text(encoding="utf-8").lower())
    corpus = "\n".join(corpus_parts)

    for requirement, markers in CORPUS_REQUIREMENTS:
        if not any(m in corpus for m in markers):
            failures.append("entry files do not establish: %s" % requirement)

    start = root / "prompts" / "00-start-here.md"
    if start.is_file():
        start_lower = start.read_text(encoding="utf-8").lower()
        for requirement, markers in START_FILE_REQUIREMENTS:
            if not any(m in start_lower for m in markers):
                failures.append("missing: %s" % requirement)

    return failures


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL agent_runnability_static_check: %s" % p)
    if not problems:
        print("PASS agent_runnability_static_check")
    sys.exit(1 if problems else 0)
