"""Static eval: Catalyst Core V1 mechanism remains present and wired."""
from pathlib import Path

REQUIRED_FILES = [
    "catalyst_core/models/core.py",
    "catalyst_core/core_store.py",
    "catalyst_core/core_engines.py",
    "docs/core-mechanism.md",
    "docs/engines.md",
    "docs/memory.md",
    "docs/loops.md",
    "docs/evals.md",
    "tests/test_core_v1.py",
]

REQUIRED_ENGINES = [
    "evidence_engine",
    "signal_extraction_engine",
    "taste_engine",
    "judgment_engine",
    "identity_engine",
    "context_engine",
    "memory_engine",
    "consolidation_engine",
    "contradiction_scope_engine",
    "retrieval_engine",
    "agent_packet_engine",
    "eval_feedback_engine",
]

REQUIRED_TYPES = [
    "evidence_item",
    "memory_atom",
    "identity_atom",
    "context_atom",
    "taste_delta",
    "taste_rule",
    "judgment_atom",
    "standard_atom",
    "anti_pattern",
    "eval_check",
    "reference_item",
    "retrieval_set",
    "agent_packet",
    "feedback_event",
    "eval_result",
    "proof_record",
    "engine_run",
]

REQUIRED_ENDPOINTS = [
    "/api/core/health",
    "/api/core/graph",
    "/api/core/engines",
    "/api/core/ingest",
    "/api/core/extract",
    "/api/core/packet",
    "/api/core/evaluate",
    "/api/core/feedback",
]


def _read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8", errors="ignore")


def run(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            failures.append(f"missing Core V1 file: {rel}")

    core = _read(root, "catalyst_core/core_engines.py") if (root / "catalyst_core/core_engines.py").is_file() else ""
    for engine in REQUIRED_ENGINES:
        if engine not in core:
            failures.append(f"missing Core V1 engine: {engine}")

    models = _read(root, "catalyst_core/models/core.py") if (root / "catalyst_core/models/core.py").is_file() else ""
    store_text = _read(root, "catalyst_core/core_store.py") if (root / "catalyst_core/core_store.py").is_file() else ""
    joined = core + "\n" + models + "\n" + store_text
    for type_name in REQUIRED_TYPES:
        if type_name not in joined:
            failures.append(f"missing Core V1 object type reference: {type_name}")

    server = _read(root, "apps/control-panel/server.py") if (root / "apps/control-panel/server.py").is_file() else ""
    for endpoint in REQUIRED_ENDPOINTS:
        if endpoint not in server:
            failures.append(f"missing Core V1 endpoint: {endpoint}")

    tests = _read(root, "tests/test_core_v1.py") if (root / "tests/test_core_v1.py").is_file() else ""
    for phrase in ["taste_delta", "judgment_atom", "anti_pattern", "eval_check", "compiled_into", "improved_by"]:
        if phrase not in tests:
            failures.append(f"Core V1 dogfood test missing proof phrase: {phrase}")

    return failures


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for problem in problems:
        print(f"FAIL core_v1_check: {problem}")
    if not problems:
        print("PASS core_v1_check")
    sys.exit(1 if problems else 0)
