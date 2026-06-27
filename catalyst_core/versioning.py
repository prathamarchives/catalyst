"""Local snapshot history for approved proposal application."""
from __future__ import annotations

import hashlib
from pathlib import Path

from . import paths, store


def _safe_history_name(text: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in text]
    out = "".join(keep)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")[:80] or "snapshot"


def snapshot_file(target: Path, proposal_id: str, reason: str, state_root: Path = store.STATE_ROOT,
                  allowed_roots: list[Path] | None = None) -> dict:
    target = target.resolve()
    roots = [Path(root).resolve() for root in (allowed_roots or [paths.OUTPUTS.resolve(), store.STATE_ROOT.resolve()])]
    if not any(_inside(target, root) for root in roots):
        return {"error": "target is outside allowed Catalyst roots"}
    text = target.read_text(encoding="utf-8") if target.is_file() else ""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    folder = store.state_path("history", state_root=state_root)
    folder.mkdir(parents=True, exist_ok=True)
    stamp = store.now_iso().replace(":", "").replace("-", "")
    snap_name = f"{stamp}-{_safe_history_name(proposal_id)}-{digest}.md"
    snap = folder / snap_name
    snap.write_text(text, encoding="utf-8")
    row = {
        "id": store.new_id("hist"),
        "proposal_id": proposal_id,
        "target": str(target),
        "snapshot": str(snap),
        "sha256": digest,
        "reason": reason,
        "created_at": store.now_iso(),
    }
    return store.append_jsonl("history/history.jsonl", row, state_root)


def list_history(limit: int = 50, state_root: Path = store.STATE_ROOT) -> list[dict]:
    return store.latest(store.read_jsonl("history/history.jsonl", state_root), limit)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False
