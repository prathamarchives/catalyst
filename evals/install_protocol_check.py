"""Eval: the repo teaches an agent to INSTALL and SET UP autonomously.

The known failure mode this guards: an agent clones the repo, sees no
package.json, concludes "nothing to install", and stops -- pushing all the
real work back onto the user. The install/setup docs must make that
impossible, and must keep user burden to approvals + feedback only.

Two layers:
1. Required markers -- the install corpus must establish the full autonomous
   install -> setup flow (repo-link, clone, no-package-install, optional eval
   verification, permission-block handling, do-not-stop-at-clone, recommended
   scan preset, one approval question, scan-only-approved-scope, provider
   caveat, minimal-burden language).
2. Bad-pattern guard -- the install-specific docs must not ASSERT the stale
   failure patterns ("no package.json, done", "scan everything automatically",
   etc.). They may QUOTE them as anti-patterns: a bad pattern on a line that
   also carries a negation marker ("do not", "never", "bad:", ...) is exempt,
   exactly like anti-slop docs are exempt in content_slop_check.
"""
from pathlib import Path

# Combined corpus for required-marker checks.
CORPUS_FILES = [
    "INSTALL.md",
    "SETUP-PROMPT.md",
    "prompts/08-install-and-run.md",
    "docs/install-vs-use.md",
    "docs/permission-model.md",
    "README.md",
    "AGENTS.md",
    "REPO-USE-PROMPT.md",
]

# Files scanned for asserted bad patterns (the install-specific docs).
BAD_PATTERN_FILES = [
    "INSTALL.md",
    "SETUP-PROMPT.md",
    "prompts/08-install-and-run.md",
    "docs/install-vs-use.md",
]

# (label, markers, mode) -- mode "any" (default) or "all".
REQUIREMENTS = [
    ("repo-link install flow", ["github.com", "repo link", "repo url"], "any"),
    ("clone/open the repo", ["clone"], "any"),
    ("no package install required", ["no package install"], "any"),
    ("do not stop at clone", ["do not stop at clone"], "any"),
    ("optional eval verification", ["py evals/run_all.py"], "any"),
    ("permission-block handling", ["blocked"], "any"),
    ("protocol install complete", ["protocol install is complete"], "any"),
    ("run setup after install", ["run setup", "creative brain setup", "next i'll run", "run the creative brain setup"], "any"),
    ("recommended scan preset", ["recommended scan"], "any"),
    ("edit + manual scan modes", ["edit scope", "manual mode"], "all"),
    ("one approval question", ["approve recommended scan"], "any"),
    ("scan only the approved scope", ["approved scope"], "any"),
    ("model/provider caveat", ["provider"], "any"),
    ("minimal user-burden language", ["user burden", "minimal burden", "almost no"], "any"),
]

# Stale/bad patterns that must never be ASSERTED as instructions.
BAD_PATTERNS = [
    "no package.json, done",
    "nothing to install, done",
    "ask the user to find their session paths",
    "scan everything automatically",
    "no approval needed",
]

# A bad pattern on a line carrying any of these is a documented anti-pattern,
# not an instruction -- exempt it.
NEGATION_MARKERS = [
    "do not", "don't", "never", "avoid", "instead",
    "bad:", "bad —", "bad -", "wrong", "failure", "❌",
]


def _read(root: Path, rel: str):
    p = root / rel
    if not p.is_file():
        return None
    return p.read_text(encoding="utf-8")


def run(root: Path) -> list:
    failures = []

    corpus_parts = []
    for rel in CORPUS_FILES:
        text = _read(root, rel)
        if text is None:
            failures.append("missing install corpus file: %s" % rel)
        else:
            corpus_parts.append(text.lower())
    corpus = "\n".join(corpus_parts)

    for label, markers, mode in REQUIREMENTS:
        if mode == "all":
            ok = all(m in corpus for m in markers)
        else:
            ok = any(m in corpus for m in markers)
        if not ok:
            failures.append("install protocol does not establish: %s" % label)

    for rel in BAD_PATTERN_FILES:
        text = _read(root, rel)
        if text is None:
            continue  # absence already reported via corpus check if required
        for i, line in enumerate(text.splitlines(), start=1):
            low = line.lower()
            negated = any(neg in low for neg in NEGATION_MARKERS)
            for bad in BAD_PATTERNS:
                if bad in low and not negated:
                    failures.append(
                        'asserted stale/bad install pattern in %s (line %d): "%s" '
                        "(quote it as an anti-pattern with a negation, or remove it)"
                        % (rel, i, bad)
                    )

    return failures


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL install_protocol_check: %s" % p)
    if not problems:
        print("PASS install_protocol_check")
    sys.exit(1 if problems else 0)
