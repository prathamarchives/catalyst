import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalyst_core import paths


def test_slug():
    assert paths.slug("Pratham!!") == "pratham"
    assert paths.slug("  Demo Flow ") == "demo-flow"
    assert paths.slug("") == "me"


def test_safe_paths(tmp_path):
    (tmp_path / "outputs" / "demo" / "catalyst-brain").mkdir(parents=True)
    o = tmp_path / "outputs"
    assert paths.brain_dir("demo", outputs_root=o) is not None
    assert paths.brain_dir("missing", outputs_root=o) is None
    assert paths.safe_brain_file("demo", "identity.md", outputs_root=o) is not None
    assert paths.safe_brain_file("demo", "../x.md", outputs_root=o) is None
    assert paths.safe_brain_file("demo", "notes.txt", outputs_root=o) is None
    assert paths.safe_outputs_path("demo/x.md", outputs_root=o) is not None
    assert paths.safe_outputs_path("../x.md", outputs_root=o) is None


def test_is_placeholder():
    tmpl = ("# judgment\n\n## evidence / rules\n\n- status: assumed\n"
            "  evidence: pending\n  rule: replace with extracted material\n")
    filled = ("# judgment\n\n## evidence / rules\n\n- status: confirmed\n"
              "  evidence: said it\n  rule: no hype words\n")
    assert paths.is_placeholder(tmpl) is True
    assert paths.is_placeholder(filled) is False


def test_parse_sections():
    text = "# t\n\n## purpose\n\nhi\n\n## evidence / rules\n\n- rule: x\n"
    secs = paths.parse_sections(text)
    assert secs["purpose"] == "hi"
    assert "rule: x" in secs["evidence / rules"]
