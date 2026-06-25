import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalyst_core import evaluator
from tests.conftest import seed_file


def test_full_report(temp_brain):
    seed_file(temp_brain, "identity.md", "builder")
    seed_file(temp_brain, "standards.md", "specific only")
    seed_file(temp_brain, "judgment.md", "ship if specific")
    rep = evaluator.evaluate_output("demo-flow-test", "write a post",
                                    "A specific, plain-spoken update on the build.",
                                    outputs_root=temp_brain["outputs_root"])
    assert rep["verdict"] in ("ship", "revise", "reject", "ask")
    for k in ["identity_alignment", "standards_match", "judgment_match", "taste_match", "anti_slop"]:
        assert 0 <= rep["scores"][k] <= 5


def test_slop_penalized(temp_brain):
    rep = evaluator.evaluate_output("demo-flow-test", "write a post",
                                    "Unlock and supercharge your seamless tapestry to elevate synergy.",
                                    outputs_root=temp_brain["outputs_root"])
    assert rep["scores"]["anti_slop"] < 5
    assert rep["issues"]
    assert rep["verdict"] in ("revise", "reject", "ask")


def test_empty_asks(temp_brain):
    rep = evaluator.evaluate_output("demo-flow-test", "write a post", "",
                                    outputs_root=temp_brain["outputs_root"])
    assert rep["verdict"] == "ask"
    assert rep["missing_context_questions"]


def test_placeholder_brain_blocks_alignment_scores(temp_brain):
    rep = evaluator.evaluate_output("demo-flow-test", "write a launch post",
                                    "Our platform helps teams unlock productivity with seamless AI workflows.",
                                    outputs_root=temp_brain["outputs_root"])
    assert rep["verdict"] == "ask"
    assert rep["scores"]["identity_alignment"] <= 1
    assert rep["scores"]["standards_match"] <= 1
    assert rep["scores"]["judgment_match"] <= 1
    assert any("blocked/limited" in issue for issue in rep["issues"])
    assert any("routed files missing/unfilled" in q for q in rep["missing_context_questions"])
    assert any("extraction" in c or "build" in c for c in rep["brain_update_candidates"])
