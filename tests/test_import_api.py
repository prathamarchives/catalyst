import importlib.util
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _load_server():
    spec = importlib.util.spec_from_file_location("catalyst_server", ROOT / "apps" / "control-panel" / "server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_import_files_confined_to_outputs():
    server = _load_server()
    slug = "zz-import-test"
    try:
        res = server._import_files(slug, [
            {"filename": "notes.md", "text": "hello"},
            {"filename": "../evil.md", "text": "nope"},
        ])
        assert res["ok"] is True
        base = ROOT / "outputs" / slug / "sources"
        assert (base / "notes.md").is_file()
        # traversal is sanitized to a basename inside the brain, never escaping outputs/
        assert not (ROOT / "outputs" / "evil.md").exists()
        assert not (ROOT / "evil.md").exists()
        for w in res["written"]:
            assert w.startswith("sources/")
    finally:
        shutil.rmtree(ROOT / "outputs" / slug, ignore_errors=True)


def test_import_extract_writes_nothing_and_returns_prompt():
    server = _load_server()
    slug = "zz-extract-test"
    try:
        res = server._import_extract(slug, "manual")
        assert "prompt" in res
        assert res["live"] is False
        assert not (ROOT / "outputs" / slug / "catalyst-brain").exists()
    finally:
        shutil.rmtree(ROOT / "outputs" / slug, ignore_errors=True)
