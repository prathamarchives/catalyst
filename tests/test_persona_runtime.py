import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalyst_core import capture, compiler, graph, health, judgment, memory, proposals, recall, store, subbrains, traces


def test_capture_pipeline_builds_runtime_state(tmp_path):
    state = tmp_path / ".catalyst"
    result = capture.capture_event({
        "type": "feedback",
        "project": "demo",
        "agent": "codex",
        "task": "write a launch post",
        "output": "Unlock seamless productivity.",
        "user_feedback": "Never use generic phrases; make launch copy concrete.",
        "outcome": "rejected",
    }, state_root=state)

    assert result["ok"] is True
    assert result["signals_created"] >= 1
    assert result["memories_created_or_updated"] >= 1
    assert result["sub_brains_affected"]
    assert result["graph_updated"] is True
    assert (state / "events" / "events.jsonl").is_file()
    assert (state / "signals" / "signals.jsonl").is_file()
    assert (state / "memories" / "memories.jsonl").is_file()
    assert (state / "persona-brain" / "_index.md").is_file()


def test_recall_judgment_health_graph(tmp_path):
    state = tmp_path / ".catalyst"
    capture.capture_event({
        "type": "correction",
        "project": "demo",
        "agent": "codex",
        "task": "write a launch post",
        "user_feedback": "Never ship copy that says unlock or seamless.",
    }, state_root=state)

    packet = recall.build_context_packet("write a launch post", project="demo", agent="codex", state_root=state)
    assert packet["task_type"] == "writing"
    assert "voice" in packet["selected_sub_brains"]
    assert len(packet["selected_sub_brains"]) < len(subbrains.get_subbrain_registry())

    review = judgment.review_output("write a launch post", "Unlock seamless AI workflows.", project="demo", state_root=state)
    assert review["passes"] is False
    assert review["failed_standards"]

    summary = graph.graph_summary("demo", state_root=state)
    assert summary["nodes"] >= 3
    assert summary["edges"] >= 2

    rep = health.get_health("demo", state_root=state)
    assert rep["events_count"] == 1
    assert rep["signals_count"] >= 1
    assert rep["memories_count"] >= 1
    assert "subbrain_maturity" in rep


def test_memory_search_routes_and_compiler_links(tmp_path):
    state = tmp_path / ".catalyst"
    capture.capture_event({
        "type": "approval",
        "project": "demo",
        "task": "product spec",
        "user_feedback": "Approved: concise technical standards and clear decision rules.",
    }, state_root=state)

    hits = memory.search_memories("technical standards", project="demo", state_root=state)
    assert hits
    routed = subbrains.get_subbrain_status("demo", state_root=state)
    assert any(v["nodes"] for v in routed.values())

    compiled = compiler.compile_persona_brain("demo", state_root=state)
    assert compiled["ok"] is True
    assert compiled["orphans"] == []
    assert compiled["dead_links"] == []


def test_proposals_and_traces(tmp_path):
    state = tmp_path / ".catalyst"
    prop = proposals.create_proposal("persona-brain/judgment/shipping-rules.md", "Add a no-generic-copy rule.", "Captured correction", state_root=state)
    assert prop["status"] == "pending"
    assert proposals.apply_proposal(prop["id"], state_root=state)["status"] == "applied"
    assert proposals.reject_proposal(prop["id"], state_root=state)["status"] == "rejected"

    trace = traces.append_trace({"agent": "codex", "task": "test", "memory_updates": ["mem_1"]}, state_root=state)
    assert trace["id"].startswith("trace_")
    assert traces.list_traces(state_root=state)[0]["id"] == trace["id"]

