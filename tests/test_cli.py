import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "catalyst_cli.py"


def run(args):
    return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True)


def test_help_lists_subcommands():
    r = run(["--help"])
    assert r.returncode == 0
    for sub in ["init", "status", "context", "route", "evaluate", "feedback", "audit"]:
        assert sub in r.stdout


def test_init_route_audit(tmp_path):
    out = tmp_path / "outputs"
    assert run(["init", "demo", "--outputs-root", str(out)]).returncode == 0
    assert (out / "demo" / "catalyst-brain" / "identity.md").is_file()
    r = run(["route", "demo", "write a dm reply", "--outputs-root", str(out), "--json"])
    assert r.returncode == 0 and "reply/dm" in r.stdout
    a = run(["audit", "demo", "--outputs-root", str(out), "--json"])
    assert a.returncode == 0 and "ready_score" in a.stdout
