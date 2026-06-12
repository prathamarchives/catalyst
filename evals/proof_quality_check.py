"""Eval: the proof loop is honest -- no strawman baselines, blind preference
testing exists, and memory has a lifecycle.

Three layers:
1. The worked before/after proof must compare against a competent baseline.
   Strawman demo phrases (fake hype no frontier model would write) are banned
   from the proof file.
2. The blind A/B protocol must exist: hidden/shuffled labels, the
   brain_win_rate metric, a no-strawman-baseline rule, and an effectiveness
   metric beyond preference.
3. The memory lifecycle must exist: distillation, stale/decay, merging
   duplicates, contradiction review. The skill template must carry quick/full
   load modes, and rejected examples must outrank banned-word lists.

Exemption: files named anti-slop.md or rejected-examples.md are never scanned
for strawman phrases (same rule as content_slop_check) -- listing bad output
is their job. The before/after proof gets no such exemption.
"""
from pathlib import Path

INSPECTED_FILES = [
    "examples/pratham-mini/before-after.md",
    "docs/blind-ab-eval.md",
    "docs/memory-lifecycle.md",
    "templates/workflows/blind-ab-test.md",
    "templates/workflows/distill-memory.md",
    "templates/skills/creative-identity-skill.md",
    "AGENTS.md",
    "prompts/09-distill-and-decay-memory.md",
    "prompts/10-run-blind-ab-proof.md",
]

# Each requirement passes if ANY marker appears (case-insensitive) in ANY of
# its files. Failures name the requirement and where it was expected.
REQUIREMENTS = [
    (
        "blind A/B protocol",
        ["docs/blind-ab-eval.md", "prompts/10-run-blind-ab-proof.md", "templates/workflows/blind-ab-test.md"],
        ["blind a/b"],
    ),
    (
        "hidden or shuffled labels",
        ["docs/blind-ab-eval.md", "prompts/10-run-blind-ab-proof.md", "templates/workflows/blind-ab-test.md"],
        ["hide and shuffle", "hidden labels", "labels stay hidden", "shuffle the labels"],
    ),
    (
        "brain_win_rate metric",
        ["docs/blind-ab-eval.md", "prompts/10-run-blind-ab-proof.md", "templates/workflows/blind-ab-test.md"],
        ["brain_win_rate"],
    ),
    (
        "competent baseline language in the worked proof",
        ["examples/pratham-mini/before-after.md"],
        ["competent"],
    ),
    (
        "no-strawman-baseline rule",
        ["docs/blind-ab-eval.md", "prompts/10-run-blind-ab-proof.md", "templates/workflows/blind-ab-test.md"],
        ["do not strawman the baseline"],
    ),
    (
        "effectiveness metric beyond preference",
        ["docs/blind-ab-eval.md", "prompts/10-run-blind-ab-proof.md", "templates/workflows/blind-ab-test.md"],
        ["effectiveness"],
    ),
    (
        "memory distillation",
        ["docs/memory-lifecycle.md", "prompts/09-distill-and-decay-memory.md", "templates/workflows/distill-memory.md"],
        ["distill"],
    ),
    (
        "memory decay language",
        ["docs/memory-lifecycle.md", "prompts/09-distill-and-decay-memory.md", "templates/workflows/distill-memory.md"],
        ["decay"],
    ),
    (
        "stale context handling",
        ["docs/memory-lifecycle.md", "prompts/09-distill-and-decay-memory.md", "templates/workflows/distill-memory.md"],
        ["stale"],
    ),
    (
        "merge duplicate rules",
        ["docs/memory-lifecycle.md", "prompts/09-distill-and-decay-memory.md", "templates/workflows/distill-memory.md"],
        ["merge duplicate"],
    ),
    (
        "contradictions trigger review",
        ["docs/memory-lifecycle.md", "prompts/09-distill-and-decay-memory.md", "templates/workflows/distill-memory.md"],
        ["contradiction"],
    ),
    (
        "quick load mode",
        ["templates/skills/creative-identity-skill.md"],
        ["quick mode"],
    ),
    (
        "full load mode",
        ["templates/skills/creative-identity-skill.md"],
        ["full mode"],
    ),
    (
        "rejected examples outrank banned words",
        [
            "AGENTS.md",
            "templates/creative-brain/anti-slop.md",
            "templates/creative-brain/rejected-examples.md",
            "prompts/03-extract-creative-identity.md",
        ],
        ["outrank"],
    ),
]

# Demo-slop no frontier model would naturally produce. A proof "winning"
# against these is a rigged proof.
STRAWMAN_PHRASES = [
    "future is here",
    "rocket emoji",
    "\U0001f680",
    "10x",
    "unlock",
    "supercharge",
    "revolutionize",
    "game-changing",
    "personalized ai is here",
]

EXEMPT_FILENAMES = {"anti-slop.md", "rejected-examples.md"}


def _read_lower(root: Path, rel: str):
    path = root / rel
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8").lower()


def run(root: Path) -> list:
    failures = []
    texts = {}

    for rel in INSPECTED_FILES:
        text = _read_lower(root, rel)
        if text is None:
            failures.append("missing required file: %s" % rel)
        else:
            texts[rel] = text

    for label, files, markers in REQUIREMENTS:
        found = False
        for rel in files:
            text = texts.get(rel)
            if text is None:
                text = _read_lower(root, rel)
                if text is not None:
                    texts[rel] = text
            if text and any(marker in text for marker in markers):
                found = True
                break
        if not found:
            failures.append(
                "missing requirement: %s (expected in one of: %s)" % (label, ", ".join(files))
            )

    for rel, text in sorted(texts.items()):
        if Path(rel).name.lower() in EXEMPT_FILENAMES:
            continue
        for phrase in STRAWMAN_PHRASES:
            if phrase in text:
                line_no = text.count("\n", 0, text.find(phrase)) + 1
                shown = "rocket emoji (U+1F680)" if phrase == "\U0001f680" else phrase
                failures.append(
                    'strawman demo phrase in %s (line %d): "%s" -- the proof must beat a competent baseline, not cartoon slop'
                    % (rel, line_no, shown)
                )

    return failures


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL proof_quality_check: %s" % p)
    if not problems:
        print("PASS proof_quality_check")
    sys.exit(1 if problems else 0)
