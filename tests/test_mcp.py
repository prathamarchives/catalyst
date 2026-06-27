import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import mcp_server


def _result(method, params=None):
    return mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}})["result"]


def test_initialize_has_instructions_and_prompts_capability():
    r = _result("initialize")
    assert r["instructions"].strip()
    assert "AGENTS.md" in r["instructions"]
    assert "prompts" in r["capabilities"]


def test_prompts_list_and_get():
    lst = _result("prompts/list")
    assert any(p["name"] == "catalyst-build-and-run" for p in lst["prompts"])
    got = _result("prompts/get", {"name": "catalyst-build-and-run"})
    assert got["messages"][0]["content"]["text"].strip()


def test_tools_still_listed():
    tools = {t["name"] for t in _result("tools/list")["tools"]}
    assert {"route_task", "get_context_packet", "review_output_against_brain",
            "append_feedback", "audit_brain", "propose_brain_update"} <= tools
    assert {"catalyst_recall", "catalyst_capture", "catalyst_search",
            "catalyst_profile", "catalyst_review", "catalyst_health",
            "catalyst_graph", "catalyst_propose_update"} <= tools
    assert {"catalyst_get_brain_context", "catalyst_evaluate_output",
            "catalyst_capture_feedback", "catalyst_propose_brain_updates",
            "catalyst_apply_brain_update", "catalyst_list_brain",
            "catalyst_get_runtime_health"} <= tools
