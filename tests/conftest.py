import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def temp_brain(tmp_path):
    """A complete throwaway brain copied from templates, under tmp outputs/."""
    outputs = tmp_path / "outputs"
    dest = outputs / "demo-flow-test"
    for sub in ["catalyst-brain", "skills", "workflows", "evals"]:
        shutil.copytree(ROOT / "templates" / sub, dest / sub)
    (dest / "README.md").write_text("# demo brain\n", encoding="utf-8")
    return {"name": "demo-flow-test", "outputs_root": outputs, "dir": dest}


def seed_file(brain: dict, filename: str, rule: str) -> None:
    """Append a seeded (non-placeholder) rule to a brain file in a temp brain."""
    p = brain["dir"] / "catalyst-brain" / filename
    block = ("\n\n## seeded from onboarding\n\n- status: observed\n"
             "  evidence: test seed\n"
             f"  rule: {rule}\n")
    p.write_text(p.read_text(encoding="utf-8") + block, encoding="utf-8")
