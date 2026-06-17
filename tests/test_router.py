import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalyst_core import router
from tests.conftest import seed_file


def test_classify():
    assert router.classify_task("write a dm reply about Catalyst")[0] == "reply/dm"
    assert router.classify_task("should I pivot the product")[0] == "strategy/decision"
    assert router.classify_task("write a launch thread")[0] == "writing/content"
    assert router.classify_task("research the memory tooling space")[0] == "research/synthesis"
    assert router.classify_task("qwerty zxcv")[0] == "unknown/high-stakes"
    assert router.classify_task("draft the investor update")[0] == "unknown/high-stakes"


def test_route_fields(temp_brain):
    seed_file(temp_brain, "identity.md", "builder, raw voice")
    r = router.route_task("demo-flow-test", "write a dm reply", outputs_root=temp_brain["outputs_root"])
    assert r["task_type"] == "reply/dm"
    assert {"task_type", "confidence", "files_to_load", "why_each_file", "missing_files", "warnings"} <= set(r)
    assert "identity.md" in r["files_to_load"] and "identity.md" in r["why_each_file"]


def test_route_flags_missing_brain():
    r = router.route_task("nobody", "write a post", outputs_root=Path("/tmp/none-xyz"))
    assert any("no brain" in w for w in r["warnings"])
