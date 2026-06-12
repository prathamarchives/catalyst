"""Eval: the protocol describes ONE consistent generated-output shape.

Drift between AGENTS.md's output structure, prompt 04's build list, prompt 05's
skill spec, the feedback-memory template, and the worked example is how a fresh
agent ends up building something that doesn't match the docs. This check keeps
them in lockstep.

Fails if:
- a canonical generated-output file is named in AGENTS.md but not created by
  prompt 04, or vice versa (covers blind-ab-test, distill-memory, blind-ab-log)
- prompt 05 omits the quick/full load modes
- the feedback-memory template omits the lifecycle sections
  (active rules / raw feedback log / retired / distillation log)
- the example skill omits quick/full modes
- README or REPO-USE-PROMPT omit the install-from-link path
"""
from pathlib import Path

AGENTS = "AGENTS.md"
PROMPT04 = "prompts/04-build-creative-brain.md"
PROMPT05 = "prompts/05-write-agent-skill.md"
FEEDBACK_TPL = "templates/creative-brain/feedback-memory.md"
EXAMPLE_SKILL = "examples/pratham-mini/skills/creative-identity-skill.md"
README = "README.md"
USE_PROMPT = "REPO-USE-PROMPT.md"

# Generated-output files that must appear in BOTH AGENTS.md and prompt 04.
OUTPUT_TOKENS = [
    "use-creative-brain",
    "update-from-feedback",
    "review-output",
    "blind-ab-test",
    "distill-memory",
    "blind-ab-log",
]

FEEDBACK_SECTIONS = ["active rules", "raw feedback log", "retired", "distillation log"]


def _read(root: Path, rel: str):
    p = root / rel
    if not p.is_file():
        return None
    return p.read_text(encoding="utf-8").lower()


def run(root: Path) -> list:
    failures = []

    agents = _read(root, AGENTS)
    p04 = _read(root, PROMPT04)
    p05 = _read(root, PROMPT05)
    fb = _read(root, FEEDBACK_TPL)
    exskill = _read(root, EXAMPLE_SKILL)
    readme = _read(root, README)
    use_prompt = _read(root, USE_PROMPT)

    for label, text in [
        (AGENTS, agents), (PROMPT04, p04), (PROMPT05, p05),
        (FEEDBACK_TPL, fb), (EXAMPLE_SKILL, exskill),
        (README, readme), (USE_PROMPT, use_prompt),
    ]:
        if text is None:
            failures.append("missing file: %s" % label)

    if agents is not None and p04 is not None:
        for token in OUTPUT_TOKENS:
            in_agents = token in agents
            in_p04 = token in p04
            if in_agents and not in_p04:
                failures.append(
                    "AGENTS.md output structure names '%s' but prompt 04 does not create it" % token
                )
            if in_p04 and not in_agents:
                failures.append(
                    "prompt 04 creates '%s' but AGENTS.md output structure omits it" % token
                )
            if not in_agents and not in_p04:
                failures.append(
                    "generated-output file '%s' is missing from both AGENTS.md and prompt 04" % token
                )

    if p05 is not None:
        for mode in ["quick mode", "full mode"]:
            if mode not in p05:
                failures.append("prompt 05 skill spec omits load mode: %s" % mode)

    if fb is not None:
        for section in FEEDBACK_SECTIONS:
            if section not in fb:
                failures.append("feedback-memory template omits lifecycle section: %s" % section)

    if exskill is not None:
        for mode in ["quick mode", "full mode"]:
            if mode not in exskill:
                failures.append("example skill omits load mode: %s" % mode)

    for label, text in [(README, readme), (USE_PROMPT, use_prompt)]:
        if text is not None and "install.md" not in text:
            failures.append("%s omits the install-from-link path (no link to INSTALL.md)" % label)

    return failures


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL output_consistency_check: %s" % p)
    if not problems:
        print("PASS output_consistency_check")
    sys.exit(1 if problems else 0)
