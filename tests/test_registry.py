import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalyst_core import registry
from tests.conftest import seed_file


def test_list_and_resolve(temp_brain):
    brains = registry.list_brains(outputs_root=temp_brain["outputs_root"])
    b = next(x for x in brains if x["name"] == "demo-flow-test")
    assert b["has_skills"] and b["has_workflows"] and b["has_evals"]
    assert "identity.md" in b["brain_present"]
    assert registry.resolve_brain("demo-flow-test", outputs_root=temp_brain["outputs_root"])["slug"] == "demo-flow-test"
    assert registry.resolve_brain("nope", outputs_root=temp_brain["outputs_root"]) is None


def test_validate(temp_brain):
    res = registry.validate_brain("demo-flow-test", outputs_root=temp_brain["outputs_root"])
    assert "identity.md" in res["present"]
    assert res["missing"] == []


def test_load_section(temp_brain):
    raw = registry.load_section("demo-flow-test", "judgment.md", outputs_root=temp_brain["outputs_root"])
    assert raw["exists"] and raw["empty"] is True
    seed_file(temp_brain, "judgment.md", "reject pitchy text")
    filled = registry.load_section("demo-flow-test", "judgment.md", outputs_root=temp_brain["outputs_root"])
    assert filled["empty"] is False
    assert filled["rel_path"] == "outputs/demo-flow-test/catalyst-brain/judgment.md"
    missing = registry.load_section("demo-flow-test", "ghost.md", outputs_root=temp_brain["outputs_root"])
    assert missing["exists"] is False and missing["empty"] is True
