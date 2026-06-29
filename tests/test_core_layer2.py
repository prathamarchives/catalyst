from __future__ import annotations

from catalyst_core import CatalystCore
from catalyst_core.domain.engines import EngineInput
from catalyst_core.engines.feedback import FeedbackLearningEngine


def core(tmp_path) -> CatalystCore:
    return CatalystCore(tmp_path / "core.sqlite3")


def test_feedback_changes_future_packet(tmp_path):
    c = core(tmp_path)

    before = c.compile_packet("Write Catalyst landing page copy", project="catalyst")
    before_packet = before["packet"]
    assert "generic SaaS slop" not in before_packet["packet"]
    assert before_packet["object_ids"] == []

    rejected_output = "Our platform helps teams unlock productivity with seamless AI workflows."
    learned = c.receive_feedback(
        before_packet["id"],
        rejected_output,
        "Reject this as generic SaaS slop. Catalyst copy must show taste, judgment, retrieval, eval, and feedback learning.",
        project="catalyst",
    )
    assert learned["feedback_event_id"].startswith("fb_")

    state = c.export_state("catalyst")
    object_types = {obj["type"] for obj in state["objects"]}
    assert {"taste_delta", "judgment_atom", "anti_pattern", "standard_atom", "eval_check"} <= object_types

    edge_types = {edge["type"] for edge in state["edges"]}
    assert {"extracted_from", "supports", "updated_by", "evaluated_by"} <= edge_types

    after = c.compile_packet("Write better Catalyst landing page copy", project="catalyst")
    after_packet = after["packet"]
    assert after_packet["object_ids"]
    assert "generic SaaS slop" in after_packet["packet"]
    assert "Catalyst public copy must name the cognitive kernel" in after_packet["packet"]
    assert after["proof"]["before_packet_id"] == before_packet["id"]
    assert after["proof"]["after_packet_id"] == after_packet["id"]

    review = c.evaluate_output(
        after_packet["id"],
        "Catalyst helps teams unlock productivity with seamless AI workflows.",
        project="catalyst",
    )
    assert review["verdict"] in {"revise", "reject"}
    assert review["failed_check_ids"]
    assert review["violated_object_ids"]

    proofs = c.export_state("catalyst")["proofs"]
    assert any(p["before_packet_id"] == before_packet["id"] and p["after_packet_id"] == after_packet["id"] for p in proofs)


def test_migrations_are_idempotent_and_fts_retrieval_works(tmp_path):
    path = tmp_path / "core.sqlite3"
    c1 = CatalystCore(path)
    c2 = CatalystCore(path)
    first_count = c2.get_health()["event_count"]
    assert first_count == 0

    packet = c2.compile_packet("Draft Catalyst copy", project="catalyst")["packet"]
    c2.receive_feedback(packet["id"], "Unlock productivity with AI workflows.", "generic SaaS slop", project="catalyst")
    retrieved = c2.retrieve_for_task("avoid generic SaaS language in Catalyst copy", project="catalyst")
    assert retrieved["candidates"]
    assert any(c["object_type"] == "anti_pattern" for c in retrieved["candidates"])

    c3 = CatalystCore(path)
    assert c3.get_health("catalyst")["object_count"] >= 5


def test_engines_can_dry_run_without_mutating_state(tmp_path):
    c = core(tmp_path)
    before = c.get_health("catalyst")["event_count"]
    packet = c.compile_packet("Write Catalyst copy", project="catalyst")["packet"]
    count_after_packet = c.get_health("catalyst")["event_count"]
    engine = FeedbackLearningEngine()
    dry = engine.run(EngineInput(
        engine_id=engine.spec.id,
        project="catalyst",
        input_ids=[packet["id"]],
        data={
            "packet": packet,
            "packet_id": packet["id"],
            "task": packet["task"],
            "output": "Unlock productivity.",
            "feedback": "generic SaaS slop",
        },
    ))
    assert dry
    assert c.get_health("catalyst")["event_count"] == count_after_packet
    assert count_after_packet > before


def test_consolidation_preserves_sources(tmp_path):
    c = core(tmp_path)
    p1 = c.compile_packet("Write Catalyst copy", project="catalyst")["packet"]
    c.receive_feedback(p1["id"], "Unlock productivity.", "generic SaaS slop", project="catalyst")
    p2 = c.compile_packet("Write Catalyst launch post", project="catalyst")["packet"]
    c.receive_feedback(p2["id"], "Seamless AI workflows.", "LinkedIn slop and generic SaaS", project="catalyst")

    consolidated = c.consolidate_project("catalyst")
    assert consolidated["created_object_ids"]
    objects = c.export_state("catalyst")["objects"]
    created = [o for o in objects if o["id"] in consolidated["created_object_ids"]]
    assert created
    assert created[0]["evidence_ids"]
    edges = c.export_state("catalyst")["edges"]
    assert any(e["type"] == "consolidates" for e in edges)


def test_contradiction_creates_scoped_exception_edge(tmp_path):
    c = core(tmp_path)
    p = c.compile_packet("Write Catalyst copy", project="catalyst")["packet"]
    c.receive_feedback(p["id"], "Unlock productivity.", "generic SaaS slop", project="catalyst")
    objects = [o for o in c.export_state("catalyst")["objects"] if o["type"] in {"anti_pattern", "standard_atom"}]
    edge = c.contradiction_runtime.mark_contradiction(objects[0]["id"], objects[1]["id"], project="catalyst", scope="internal notes")
    assert edge["type"] == "contradicts"


def test_packet_compiler_does_not_dump_all_memory(tmp_path):
    c = core(tmp_path)
    packet = c.compile_packet("Write Catalyst copy", project="catalyst")["packet"]
    for i in range(8):
        c.receive_feedback(
            packet["id"],
            f"Generic output {i}: unlock productivity.",
            f"generic SaaS slop signal {i}",
            project="catalyst",
        )
    next_packet = c.compile_packet("Write Catalyst launch copy", project="catalyst", limit=5)["packet"]
    assert len(next_packet["object_ids"]) <= 5
    assert "not a memory dump" in next_packet["packet"]

