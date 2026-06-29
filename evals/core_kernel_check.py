"""Static checks for the Layer 2 kernel boundary."""
from __future__ import annotations

from pathlib import Path


REQUIRED_FILES = [
    "catalyst_core/domain/events.py",
    "catalyst_core/domain/objects.py",
    "catalyst_core/storage/sqlite_store.py",
    "catalyst_core/kernel/mutation_runtime.py",
    "catalyst_core/kernel/retrieval_planner.py",
    "catalyst_core/kernel/packet_compiler.py",
    "catalyst_core/kernel/eval_runtime.py",
    "catalyst_core/kernel/feedback_learner.py",
    "catalyst_core/api/core_api.py",
    "tests/test_core_layer2.py",
]

FORBIDDEN_PATHS = [
    "apps/web",
    "packages/cli",
    "tools/mcp_server.py",
    "templates/catalyst-brain",
]

REQUIRED_README_PHRASES = [
    "cognitive kernel",
    "SQLite event store",
    "feedback changes future behavior",
    "```mermaid",
]


def run(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            failures.append(f"missing required kernel file: {rel}")
    for rel in FORBIDDEN_PATHS:
        if (root / rel).exists():
            failures.append(f"old product surface still present: {rel}")
    readme = (root / "README.md").read_text(encoding="utf-8", errors="ignore") if (root / "README.md").is_file() else ""
    for phrase in REQUIRED_README_PHRASES:
        if phrase not in readme:
            failures.append(f"README missing phrase: {phrase}")
    core = (root / "catalyst_core/kernel/mutation_runtime.py").read_text(encoding="utf-8", errors="ignore")
    if "Engines never write" in readme and "ProposedMutation" not in core:
        failures.append("mutation runtime does not expose ProposedMutation boundary")
    return failures


if __name__ == "__main__":
    problems = run(Path(__file__).resolve().parents[1])
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        raise SystemExit(1)
    print("PASS: Core Layer 2 kernel boundary is present")

