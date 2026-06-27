import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalyst_core import (
    brain_parser,
    context_assembler,
    feedback_processor,
    proposal_engine,
    structured_evaluator,
    versioning,
)
from tests.conftest import seed_file


def test_brain_parser_preserves_freeform_markdown_and_extracts_rules():
    text = """# Standards

## evidence / rules

- rule: Always anchor claims in concrete proof.
- decision: Ship only when examples are specific.

## odd local note

Keep this exact freeform note even if the parser does not understand it.
"""
    section = brain_parser.parse_brain_section("standards.md", text, "outputs/demo/catalyst-brain/standards.md")

    assert section.status == "active"
    assert section.raw_markdown == text
    assert "odd local note" in section.unknown_markdown
    assert any("concrete proof" in standard.text for standard in section.standards)


def test_feedback_processor_classifies_and_creates_update_proposals(tmp_path):
    state = tmp_path / ".catalyst"
    result = feedback_processor.capture_feedback_structured(
        "write a launch post",
        "Unlock seamless productivity.",
        "Never use unlock or seamless; make launch copy concrete.",
        project="demo",
        source="test",
        state_root=state,
    )

    assert result["ok"] is True
    assert result["feedback_type"] == "rejected_pattern"
    assert {"judgment", "rejected-examples", "anti-slop"} <= set(result["target_sections"])
    assert result["signal_ids"]
    assert result["memory_ids"]
    assert len(result["proposal_ids"]) >= 1


def test_structured_evaluator_is_low_confidence_on_placeholder_brain(tmp_path, temp_brain):
    state = tmp_path / ".catalyst"
    result = structured_evaluator.evaluate_output_structured(
        "write a launch post",
        "Our platform helps teams unlock productivity with seamless AI workflows.",
        project=temp_brain["name"],
        state_root=state,
        outputs_root=temp_brain["outputs_root"],
    )

    assert result["verdict"] == "ask"
    assert result["confidence"] <= 0.45
    assert "standards_alignment" in result["scores"]
    assert any("blocked/limited" in issue["message"] for issue in result["issues"])


def test_structured_evaluator_detects_rejected_pattern(tmp_path, temp_brain):
    state = tmp_path / ".catalyst"
    seed_file(temp_brain, "rejected-examples.md", "never say unlock productivity")
    result = structured_evaluator.evaluate_output_structured(
        "write a launch post",
        "Never say unlock productivity.",
        project=temp_brain["name"],
        state_root=state,
        outputs_root=temp_brain["outputs_root"],
    )

    assert result["scores"]["rejected_pattern_risk"] == 0.0
    assert result["violated_patterns"]
    assert any(issue["dimension"] == "rejected_pattern_risk" for issue in result["issues"])


def test_context_assembler_returns_compact_packet(tmp_path, temp_brain):
    state = tmp_path / ".catalyst"
    seed_file(temp_brain, "standards.md", "launch copy must include concrete proof")
    seed_file(temp_brain, "judgment.md", "revise if the draft sounds generic")
    result = feedback_processor.capture_feedback_structured(
        "write a launch post",
        "Generic AI workflow copy.",
        "Approved: concrete proof and direct product language works.",
        project=temp_brain["name"],
        state_root=state,
    )
    packet = context_assembler.assemble_context(
        "write a launch post",
        project=temp_brain["name"],
        agent="test",
        state_root=state,
        outputs_root=temp_brain["outputs_root"],
    )

    assert result["proposal_ids"]
    assert packet["task_type"] == "writing"
    assert packet["standards"]
    assert packet["judgment_rules"]
    assert len(packet["sections_loaded"]) < 10
    assert len(packet["memory_atoms"]) <= 12


def test_apply_brain_update_writes_history_and_appends_only(tmp_path, temp_brain):
    state = tmp_path / ".catalyst"
    prop = proposal_engine.create_brain_update(
        temp_brain["name"],
        "judgment",
        "Never ship copy that says unlock or seamless.",
        "captured correction",
        confidence=0.8,
        state_root=state,
    )
    applied = proposal_engine.apply_brain_update(
        prop["id"],
        project=temp_brain["name"],
        outputs_root=temp_brain["outputs_root"],
        state_root=state,
    )

    target = temp_brain["dir"] / "catalyst-brain" / "judgment.md"
    assert applied["ok"] is True
    assert "applied Catalyst proposal" in target.read_text(encoding="utf-8")
    history = versioning.list_history(state_root=state)
    assert history
    assert history[0]["proposal_id"] == prop["id"]
