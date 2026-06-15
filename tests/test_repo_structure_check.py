from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evals"))

import repo_structure_check


def write_required_files(root: Path) -> None:
    for rel in repo_structure_check.REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".md":
            path.write_text((f"# {rel}\n\n" + "real content for structure test. ") * 8, encoding="utf-8")
        else:
            path.write_text("placeholder\n", encoding="utf-8")


def test_repo_structure_allows_post_install_outputs(tmp_path):
    write_required_files(tmp_path)
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    (outputs / ".gitkeep").write_text("", encoding="utf-8")
    install_output = outputs / "synthetic-user"
    (install_output / "catalyst-brain").mkdir(parents=True)
    (install_output / "skills").mkdir()
    (install_output / "workflows").mkdir()
    (install_output / "evals").mkdir()
    (install_output / "README.md").write_text("# installed catalyst brain\n", encoding="utf-8")

    failures = repo_structure_check.run(tmp_path)

    assert "outputs/ must contain only .gitkeep" not in failures
    assert failures == []
