"""Eval: banned/weak phrases and overclaims stay out of the repo's own prose.

Exemption: files named anti-slop.md or rejected-examples.md are skipped --
listing banned phrases is their documented purpose. Eval design must never
make anti-slop documentation impossible.
"""
from pathlib import Path

BANNED_PHRASES = [
    "unlock",
    "supercharge",
    "all-in-one",
    "revolutionize",
    "copilot for content",
    "ai writes like you instantly",
    "purple gradient",
    "content calendar",
    "dashboard",
    "saas boilerplate",
    "10x your content",
    "just prompt better",
]

OVERCLAIMS = [
    "automatically scans all your private sessions",
    "connects to every account",
    "no setup needed",
    "guaranteed to sound like you",
    "perfectly captures your voice",
]

EXEMPT_FILENAMES = {"anti-slop.md", "rejected-examples.md"}

SCAN_TARGETS = [
    "README.md",
    "AGENTS.md",
    "REPO-USE-PROMPT.md",
    "prompts",
    "templates",
    "docs",
]


def _iter_files(root: Path):
    for target in SCAN_TARGETS:
        path = root / target
        if path.is_file():
            yield path
        elif path.is_dir():
            for md in sorted(path.rglob("*.md")):
                yield md


def run(root: Path) -> list:
    failures = []
    for path in _iter_files(root):
        if path.name.lower() in EXEMPT_FILENAMES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            failures.append("could not read %s: %s" % (path.relative_to(root).as_posix(), exc))
            continue
        lower = text.lower()
        rel = path.relative_to(root).as_posix()
        for phrase in BANNED_PHRASES:
            if phrase in lower:
                line_no = _first_line(lower, phrase)
                failures.append(
                    'banned phrase found in %s (line %d): "%s"' % (rel, line_no, phrase)
                )
        for phrase in OVERCLAIMS:
            if phrase in lower:
                line_no = _first_line(lower, phrase)
                failures.append(
                    'overclaim found in %s (line %d): "%s"' % (rel, line_no, phrase)
                )
    return failures


def _first_line(lower_text: str, phrase: str) -> int:
    index = lower_text.find(phrase)
    return lower_text.count("\n", 0, index) + 1


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL content_slop_check: %s" % p)
    if not problems:
        print("PASS content_slop_check")
    sys.exit(1 if problems else 0)
