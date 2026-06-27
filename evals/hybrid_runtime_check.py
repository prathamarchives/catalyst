"""Static eval: hybrid runtime artifacts stay present and wired."""
from pathlib import Path

REQUIRED_FILES = [
    "catalyst_core/models/brain.py",
    "catalyst_core/models/events.py",
    "catalyst_core/models/evals.py",
    "catalyst_core/models/mcp.py",
    "catalyst_core/brain_manager.py",
    "catalyst_core/brain_parser.py",
    "catalyst_core/context_assembler.py",
    "catalyst_core/structured_evaluator.py",
    "catalyst_core/feedback_processor.py",
    "catalyst_core/proposal_engine.py",
    "catalyst_core/versioning.py",
    "catalyst_core/retrieval.py",
    "catalyst_core/index.py",
    "catalyst_core/mcp_tools.py",
    "docs/hybrid-brain-runtime.md",
]

REQUIRED_MODELS = [
    "BrainProfile",
    "BrainSection",
    "Standard",
    "JudgmentRule",
    "RejectedPattern",
    "ApprovedExample",
    "FeedbackMemory",
    "TaskPattern",
    "DecisionRule",
    "ContextSource",
    "MemoryAtom",
    "Signal",
    "UpdateProposal",
    "EvalResult",
    "EvalIssue",
    "RuntimeHealth",
]

REQUIRED_MCP_TOOLS = [
    "catalyst_get_brain_context",
    "catalyst_evaluate_output",
    "catalyst_capture_feedback",
    "catalyst_propose_brain_updates",
    "catalyst_apply_brain_update",
    "catalyst_list_brain",
    "catalyst_get_runtime_health",
]

REQUIRED_HTTP = [
    "/api/brain/context",
    "/api/evaluate",
    "/api/feedback",
    "/api/proposals",
    "/api/proposals/apply",
    "/api/runtime/health",
    "/api/brain/sections",
]


def _read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8", errors="ignore")


def run(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            failures.append(f"missing hybrid runtime file: {rel}")

    joined_models = "\n".join(
        _read(root, rel)
        for rel in ["catalyst_core/models/brain.py", "catalyst_core/models/events.py", "catalyst_core/models/evals.py"]
        if (root / rel).is_file()
    )
    for name in REQUIRED_MODELS:
        if f"class {name}" not in joined_models:
            failures.append(f"missing model class: {name}")

    mcp_text = _read(root, "tools/mcp_server.py") if (root / "tools/mcp_server.py").is_file() else ""
    for tool in REQUIRED_MCP_TOOLS:
        if tool not in mcp_text:
            failures.append(f"missing rich MCP tool: {tool}")

    server_text = _read(root, "apps/control-panel/server.py") if (root / "apps/control-panel/server.py").is_file() else ""
    docs_text = _read(root, "docs/hybrid-brain-runtime.md") if (root / "docs/hybrid-brain-runtime.md").is_file() else ""
    for endpoint in REQUIRED_HTTP:
        if endpoint not in server_text:
            failures.append(f"missing HTTP endpoint: {endpoint}")
        if endpoint not in docs_text:
            failures.append(f"hybrid runtime doc does not mention endpoint: {endpoint}")

    required_tests = [
        "test_feedback_processor_classifies_and_creates_update_proposals",
        "test_structured_evaluator_is_low_confidence_on_placeholder_brain",
        "test_context_assembler_returns_compact_packet",
        "test_apply_brain_update_writes_history_and_appends_only",
    ]
    tests_text = _read(root, "tests/test_hybrid_runtime.py") if (root / "tests/test_hybrid_runtime.py").is_file() else ""
    for test_name in required_tests:
        if test_name not in tests_text:
            failures.append(f"missing regression test: {test_name}")

    return failures


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for problem in problems:
        print(f"FAIL hybrid_runtime_check: {problem}")
    if not problems:
        print("PASS hybrid_runtime_check")
    sys.exit(1 if problems else 0)
