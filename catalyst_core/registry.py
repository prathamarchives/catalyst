"""registry.py — list, resolve, validate brains and load one section safely."""
from __future__ import annotations

from pathlib import Path

from . import paths


def list_brains(outputs_root: Path = paths.OUTPUTS) -> list:
    root = Path(outputs_root)
    brains: list = []
    if not root.is_dir():
        return brains
    for child in sorted(root.iterdir()):
        if child.name == ".gitkeep" or not child.is_dir():
            continue
        bd = child / "catalyst-brain"
        present, missing = [], []
        for f in paths.BRAIN_FILE_ORDER:
            (present if (bd / f).is_file() else missing).append(f)
        brains.append({
            "name": child.name,
            "path": str(child),
            "brain_present": present if bd.is_dir() else [],
            "brain_missing": missing if bd.is_dir() else list(paths.BRAIN_FILE_ORDER),
            "has_skills": (child / "skills").is_dir(),
            "has_workflows": (child / "workflows").is_dir(),
            "has_evals": (child / "evals").is_dir(),
        })
    return brains


def resolve_brain(name: str, outputs_root: Path = paths.OUTPUTS) -> dict | None:
    bd = paths.brain_dir(name, outputs_root)
    if bd is None:
        return None
    return {"name": name, "slug": paths.slug(name), "root": bd.parent,
            "brain_dir": bd, "outputs_root": Path(outputs_root)}


def validate_brain(name: str, outputs_root: Path = paths.OUTPUTS) -> dict:
    bd = paths.brain_dir(name, outputs_root)
    if bd is None:
        return {"ok": False, "error": f"no brain for '{name}'",
                "present": [], "missing": list(paths.BRAIN_FILE_ORDER)}
    present, missing = [], []
    for f in paths.BRAIN_FILE_ORDER:
        (present if (bd / f).is_file() else missing).append(f)
    return {"ok": not missing, "present": present, "missing": missing}


def load_section(name: str, section: str, outputs_root: Path = paths.OUTPUTS) -> dict:
    p = paths.safe_brain_file(name, section, outputs_root)
    if p is None or not p.is_file():
        return {"file": section, "exists": False, "empty": True,
                "content": "", "sections": {}, "rel_path": None}
    text = p.read_text(encoding="utf-8")
    return {"file": section, "exists": True,
            "empty": paths.is_placeholder(text), "content": text,
            "sections": paths.parse_sections(text),
            "rel_path": f"outputs/{paths.slug(name)}/catalyst-brain/{section}"}
