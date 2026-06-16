"""Eval: the README/landing keep Catalyst's judgment positioning, not a
flat "memory / profile file" framing.

Guards against regressions that would make Catalyst look like a one-file
context tool: hiding judgment/feedback/evals, dropping the comparison, or
re-pitching it as "AI that writes like you".
"""
from pathlib import Path


def _read(root: Path, rel: str) -> str:
    p = root / rel
    return p.read_text(encoding="utf-8").lower() if p.is_file() else ""


def run(root: Path) -> list:
    failures = []
    readme = _read(root, "README.md")
    surface = _read(root, "docs/product-surface.md")
    agents = _read(root, "AGENTS.md")
    corpus = "\n".join([readme, surface, agents])

    # 1. the explicit comparison to one-file context tools must be present
    if "one-file context tools" not in readme:
        failures.append("README missing the 'one-file context tools' comparison framing")

    # 2. the positioning line must be preserved somewhere
    if "approve, reject, revise" not in corpus:
        failures.append("core positioning line ('approve, reject, revise, and remember') missing from README/product-surface/AGENTS")

    # 3. README must not hide the differentiators
    for term in ["judgment", "standards", "feedback", "reject"]:
        if term not in readme:
            failures.append(f"README hides a differentiator: '{term}'")

    # 4. the loop / task-time evaluation must be visible
    if not any(m in corpus for m in ["task-time evaluation", "review against", "the proof is the loop"]):
        failures.append("README/landing does not surface the task-time judgment loop")

    # 5. rejected examples must be part of the story
    if not any(m in corpus for m in ["rejected examples", "rejected-examples"]):
        failures.append("README/landing does not mention rejected examples")

    # 6. must not reduce Catalyst to a profile / memory / write-like-you PITCH.
    # Disavowals ("not 'AI that writes like you'") are fine and expected, so a
    # phrase only counts if its line is not negated.
    reductive = [
        "catalyst is just a profile",
        "catalyst is only a context file",
        "single profile file",
        "ai that writes like you",
        "just a memory app",
        "write like you",
    ]
    negations = ("not ", "isn't", "is not", "never", "no ", "instead of", "rather than", "more than")
    for line in corpus.splitlines():
        for phrase in reductive:
            if phrase in line and not any(n in line for n in negations):
                failures.append(f"reductive positioning pitched (not disavowed): '{phrase}'")

    return failures


if __name__ == "__main__":
    import sys
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL positioning_check:", p)
    if not problems:
        print("PASS positioning_check")
    sys.exit(1 if problems else 0)
