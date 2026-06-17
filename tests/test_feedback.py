import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalyst_core import feedback


def test_writes_only_under_outputs(temp_brain):
    res = feedback.capture_feedback("demo-flow-test", "write a dm reply", "draft",
                                    "too pitchy, sounds like a sales pitch",
                                    outputs_root=temp_brain["outputs_root"])
    assert res["ok"] is True
    assert res["change_type"] in ("add", "refine", "retire")
    for w in res["written"]:
        assert w.startswith("outputs/demo-flow-test/")
    assert "too pitchy" in (temp_brain["dir"] / "catalyst-brain" / "feedback-memory.md").read_text(encoding="utf-8")
    assert "user feedback: too pitchy" in (temp_brain["dir"] / "evals" / "improvement-log.md").read_text(encoding="utf-8")
    props = list((temp_brain["dir"] / "proposals").glob("*-feedback-update.md"))
    assert len(props) == 1
    assert "needs confirmation" in props[0].read_text(encoding="utf-8").lower()


def test_does_not_touch_core_rule_files(temp_brain):
    before = (temp_brain["dir"] / "catalyst-brain" / "judgment.md").read_text(encoding="utf-8")
    feedback.capture_feedback("demo-flow-test", "write a post", "d", "wrong tone",
                              outputs_root=temp_brain["outputs_root"])
    after = (temp_brain["dir"] / "catalyst-brain" / "judgment.md").read_text(encoding="utf-8")
    assert before == after


def test_missing_brain_errors():
    res = feedback.capture_feedback("ghost", "x", "y", "z", outputs_root=Path("/tmp/none-xyz"))
    assert "error" in res
