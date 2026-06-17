import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalyst_core import quality
from tests.conftest import seed_file


def test_fresh_brain_is_mostly_unfilled(temp_brain):
    rep = quality.audit_brain("demo-flow-test", outputs_root=temp_brain["outputs_root"])
    assert rep["ready_score"] < 0.4
    assert "judgment.md" in rep["flags"]


def test_seeding_raises_readiness(temp_brain):
    long_rule = "a concrete, specific extracted rule that is long enough to not be thin " * 3
    for f in ["identity.md", "standards.md", "judgment.md", "taste.md", "voice.md"]:
        seed_file(temp_brain, f, long_rule)
    rep = quality.audit_brain("demo-flow-test", outputs_root=temp_brain["outputs_root"])
    assert rep["filled"] >= 5
    assert "judgment.md" not in rep["flags"]


def test_missing_brain():
    assert quality.audit_brain("ghost", outputs_root=Path("/tmp/none-xyz")).get("error")
