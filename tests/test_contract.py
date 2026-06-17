import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalyst_core import contract, router
from tests.conftest import seed_file


def test_contract_has_core_rules(temp_brain):
    r = router.route_task("demo-flow-test", "write a post", outputs_root=temp_brain["outputs_root"])
    block = contract.build_contract("demo-flow-test", "writing/content", r, outputs_root=temp_brain["outputs_root"])
    assert "## agent judgment contract" in block
    assert "ship, revise, reject, or ask" in block
    assert "sharper, not longer" in block.lower()


def test_contract_pulls_brain_hard_nos(temp_brain):
    seed_file(temp_brain, "rejected-examples.md", "never open with a rhetorical question")
    r = router.route_task("demo-flow-test", "write a post", outputs_root=temp_brain["outputs_root"])
    block = contract.build_contract("demo-flow-test", "writing/content", r, outputs_root=temp_brain["outputs_root"])
    assert "rhetorical question" in block
