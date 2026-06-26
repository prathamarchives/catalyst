"""Local JSON/JSONL storage helpers for the Catalyst runtime.

All default writes stay inside .catalyst/. Tests can pass an alternate
state_root. No network, no database, no arbitrary paths.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from . import paths

STATE_ROOT = paths.REPO_ROOT / ".catalyst"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def state_path(*parts: str, state_root: Path = STATE_ROOT) -> Path:
    root = Path(state_root).resolve()
    target = root.joinpath(*parts).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise ValueError("state path escaped .catalyst")
    return target


def ensure_state(state_root: Path = STATE_ROOT) -> Path:
    root = Path(state_root)
    for rel in [
        ("events",),
        ("signals",),
        ("memories",),
        ("persona",),
        ("graph",),
        ("traces",),
        ("proposals",),
        ("logs",),
        ("persona-brain",),
    ]:
        state_path(*rel, state_root=root).mkdir(parents=True, exist_ok=True)
    return root


def append_jsonl(rel: str, row: dict, state_root: Path = STATE_ROOT) -> dict:
    ensure_state(state_root)
    path = state_path(*rel.split("/"), state_root=state_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.open("a", encoding="utf-8").write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return row


def read_jsonl(rel: str, state_root: Path = STATE_ROOT) -> list[dict]:
    path = state_path(*rel.split("/"), state_root=state_root)
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def write_json(rel: str, data: dict, state_root: Path = STATE_ROOT) -> dict:
    ensure_state(state_root)
    path = state_path(*rel.split("/"), state_root=state_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data


def read_json(rel: str, default=None, state_root: Path = STATE_ROOT):
    path = state_path(*rel.split("/"), state_root=state_root)
    if not path.is_file():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except ValueError:
        return {} if default is None else default


def filter_rows(rows: Iterable[dict], project: str | None = None) -> list[dict]:
    if not project:
        return list(rows)
    return [r for r in rows if (r.get("project") or "default") == project]


def latest(rows: Iterable[dict], limit: int = 50) -> list[dict]:
    return sorted(rows, key=lambda r: r.get("created_at") or r.get("updated_at") or "", reverse=True)[:limit]

