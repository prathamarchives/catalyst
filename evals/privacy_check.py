"""Eval: privacy commitments are present and uncontradicted.

Checks docs/privacy.md, README.md, AGENTS.md and .gitignore for the
required privacy language, and scans for overclaim/scraping language
that would contradict it.
"""
from pathlib import Path

PRIVACY_DOC_REQUIRED = [
    ("local-first", ["local-first"]),
    ("user controls files", ["you control", "user controls"]),
    ("no cloud upload by default", ["no cloud upload"]),
    ("outputs are gitignored", ["gitignored", "gitignore"]),
    ("secrets warning", ["secrets"]),
    ("client data warning", ["client data"]),
    ("private DMs warning", ["private dms"]),
    ("review before sharing", ["review before sharing", "review every file", "read through every generated file"]),
]

README_REQUIRED = [
    ("local-first", ["local-first"]),
    ("outputs are gitignored", ["gitignored"]),
    ("user controls the scan", ["you control", "user controls", "files and folders you point it at"]),
]

AGENTS_REQUIRED = [
    ("privacy section", ["## privacy"]),
    ("local-first", ["local-first"]),
    ("secrets/client-data handling", ["secrets"]),
]

GITIGNORE_REQUIRED_LINES = ["outputs/**", "!outputs/.gitkeep"]

# Language that would contradict the privacy stance if stated as a capability.
CONTRADICTIONS = [
    "automatically scans all your private sessions",
    "connects to every account",
    "scans everything automatically",
]


def _check(path: Path, requirements, label, failures):
    if not path.is_file():
        failures.append("%s is missing" % label)
        return
    lower = path.read_text(encoding="utf-8").lower()
    for item, markers in requirements:
        if not any(m in lower for m in markers):
            failures.append("%s missing privacy language: %s" % (label, item))


def run(root: Path) -> list:
    failures = []

    _check(root / "docs" / "privacy.md", PRIVACY_DOC_REQUIRED, "docs/privacy.md", failures)
    _check(root / "README.md", README_REQUIRED, "README.md", failures)
    _check(root / "AGENTS.md", AGENTS_REQUIRED, "AGENTS.md", failures)

    gitignore = root / ".gitignore"
    if not gitignore.is_file():
        failures.append(".gitignore is missing")
    else:
        lines = [ln.strip() for ln in gitignore.read_text(encoding="utf-8").splitlines()]
        for required in GITIGNORE_REQUIRED_LINES:
            if required not in lines:
                failures.append(".gitignore missing required line: %s" % required)

    for rel in ["README.md", "AGENTS.md", "docs/privacy.md", "docs/philosophy.md", "docs/roadmap.md"]:
        path = root / rel
        if not path.is_file():
            continue
        lower = path.read_text(encoding="utf-8").lower()
        for phrase in CONTRADICTIONS:
            if phrase in lower:
                failures.append(
                    'privacy contradiction in %s: claims "%s"' % (rel, phrase)
                )

    return failures


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL privacy_check: %s" % p)
    if not problems:
        print("PASS privacy_check")
    sys.exit(1 if problems else 0)
