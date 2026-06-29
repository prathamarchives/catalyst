import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalyst_core import core_engines


def test_core_v1_dogfood_workflow_creates_objects_graph_packet_feedback_and_proof(tmp_path):
    state = tmp_path / ".catalyst"
    evidence = core_engines.ingest_evidence(
        "Rejected: this makes Catalyst sound like a generic productivity platform. "
        "Never use unlock productivity or seamless AI workflow framing.",
        evidence_type="feedback_event",
        source="dogfood",
        project="catalyst",
        task_type="writing",
        outcome="rejected",
        state_root=state,
    )
    extraction = core_engines.run_extraction(evidence["id"], project="catalyst", state_root=state)

    created_types = {obj["type"] for obj in extraction["objects_created"]}
    assert {"taste_delta", "judgment_atom", "anti_pattern", "standard_atom", "eval_check"} <= created_types

    packet = core_engines.compile_agent_packet("improve Catalyst landing page", project="catalyst", state_root=state)
    packet_text = packet["packet"]["packet"]
    assert "ANTI-PATTERNS" in packet_text
    assert "EVAL CHECKS" in packet_text
    assert packet["packet"]["object_ids"]

    review = core_engines.evaluate_output(
        packet["packet"]["id"],
        "Unlock productivity with seamless AI workflows.",
        project="catalyst",
        state_root=state,
    )
    assert review["verdict"] in {"revise", "reject"}
    assert review["issues"]

    feedback = core_engines.capture_feedback(
        packet["packet"]["id"],
        "Unlock productivity with seamless AI workflows.",
        "Reject this generic SaaS framing. It should be about compounding judgment, taste, and agent improvement.",
        project="catalyst",
        state_root=state,
    )
    assert feedback["ok"] is True
    assert feedback["proof"]["id"].startswith("proof_")

    graph = core_engines.graph("catalyst", state_root=state)
    edge_types = {edge["type"] for edge in graph["edges"]}
    assert {"extracted_from", "retrieved_for", "compiled_into", "evaluated_by", "improved_by"} <= edge_types

    health = core_engines.health("catalyst", state_root=state)
    assert health["evidence_count"] >= 2
    assert health["memory_count"] >= 5
    assert health["packet_count"] == 1
    assert health["proof_count"] == 1
    assert health["engine_count"] == 12


def test_core_v1_engine_specs_cover_required_engines_and_memory_types():
    specs = core_engines.engine_specs()
    ids = {spec["id"] for spec in specs}
    assert len(specs) == 12
    assert {
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
    } == ids
    for spec in specs:
        assert spec["purpose"]
        assert spec["inputs"]
        assert spec["outputs"]
        assert spec["eval_hooks"]
        assert spec["health_metrics"]
        assert spec["failure_modes"]
    assert set(core_engines.MEMORY_TYPES) == {
        "episodic",
        "semantic",
        "procedural",
        "preference",
        "negative",
        "reference",
        "social_customer",
        "strategic",
    }
