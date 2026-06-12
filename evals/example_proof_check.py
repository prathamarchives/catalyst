"""Eval: the worked example contains a real, complete before/after proof.

Requires all six sections in examples/pratham-mini/before-after.md and
verifies the generic output and creative brain output are not identical.
"""
import re
from pathlib import Path

PROOF_PATH = "examples/pratham-mini/before-after.md"

REQUIRED_SECTIONS = [
    "task",
    "generic output",
    "creative brain output",
    "what changed",
    "user feedback",
    "feedback memory update",
]


def _split_sections(text: str) -> dict:
    """Map lowercase heading text -> section body."""
    sections = {}
    current = None
    body = []
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.*)$", line.strip())
        if match:
            if current is not None:
                sections[current] = "\n".join(body).strip()
            current = match.group(1).strip().lower()
            body = []
        else:
            body.append(line)
    if current is not None:
        sections[current] = "\n".join(body).strip()
    return sections


def _normalize(text: str) -> str:
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", text).strip().lower()


def run(root: Path) -> list:
    proof = root / PROOF_PATH
    if not proof.is_file():
        return ["%s is missing" % PROOF_PATH]

    text = proof.read_text(encoding="utf-8")
    sections = _split_sections(text)

    failures = []
    for required in REQUIRED_SECTIONS:
        matches = [key for key in sections if required in key]
        if not matches:
            failures.append("%s missing section: %s" % (PROOF_PATH, required))
        elif not sections[matches[0]]:
            failures.append("%s section is empty: %s" % (PROOF_PATH, required))

    generic_keys = [k for k in sections if "generic output" in k]
    brain_keys = [k for k in sections if "creative brain output" in k]
    if generic_keys and brain_keys:
        generic = _normalize(sections[generic_keys[0]])
        brain = _normalize(sections[brain_keys[0]])
        if generic and brain and generic == brain:
            failures.append(
                "%s: generic output and creative brain output are identical -- the proof proves nothing"
                % PROOF_PATH
            )
    return failures


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL example_proof_check: %s" % p)
    if not problems:
        print("PASS example_proof_check")
    sys.exit(1 if problems else 0)
