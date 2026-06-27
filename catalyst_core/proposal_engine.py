"""Structured update proposal lifecycle."""
from __future__ import annotations

from pathlib import Path

from . import paths, proposals, store, versioning


def create_brain_update(project: str, target_section: str, proposed_change: str, reason: str,
                        source_event_id: str | None = None, source_memory_id: str | None = None,
                        confidence: float = 0.6, state_root: Path = store.STATE_ROOT) -> dict:
    section = target_section if target_section.endswith(".md") else f"{target_section}.md"
    target_file = f"catalyst-brain/{section}"
    prop = proposals.create_proposal(
        target_file=target_file,
        proposed_change=proposed_change,
        reason=reason,
        source_event_id=source_event_id,
        source_memory_id=source_memory_id,
        target_brain=section.replace(".md", ""),
        project=project,
        confidence=confidence,
        state_root=state_root,
    )
    return prop


def list_brain_updates(project: str | None = None, status: str | None = "pending",
                       limit: int = 50, state_root: Path = store.STATE_ROOT) -> list[dict]:
    rows = proposals.list_proposals(status=status or None, project=project, state_root=state_root)
    return rows[: max(1, min(200, int(limit or 50)))]


def apply_brain_update(proposal_id: str, project: str = "default", approve: bool = True,
                       outputs_root: Path = paths.OUTPUTS, state_root: Path = store.STATE_ROOT) -> dict:
    rows = proposals.list_proposals(status=None, project=None, state_root=state_root)
    current = next((p for p in rows if p.get("id") == proposal_id), None)
    if not current:
        return {"error": f"proposal not found: {proposal_id}"}
    if not approve:
        return proposals.reject_proposal(proposal_id, state_root=state_root)
    rel = str(current.get("target_file") or "").replace("\\", "/").lstrip("/")
    if ".." in rel.split("/") or not rel.endswith(".md"):
        return {"error": "proposal target is not an allowed markdown file"}
    owner = current.get("project") or project or "default"
    base = (outputs_root / paths.slug(owner)).resolve()
    target = (base / rel).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        return {"error": "proposal target escaped project outputs"}
    target.parent.mkdir(parents=True, exist_ok=True)
    snapshot = versioning.snapshot_file(
        target,
        proposal_id,
        current.get("reason", ""),
        state_root=state_root,
        allowed_roots=[Path(outputs_root).resolve(), Path(state_root).resolve()],
    )
    if snapshot.get("error"):
        return snapshot
    existing = target.read_text(encoding="utf-8") if target.is_file() else f"# {target.stem}\n"
    block = (
        "\n\n## applied Catalyst proposal\n\n"
        f"- proposal_id: {proposal_id}\n"
        f"- reason: {current.get('reason', '')}\n"
        f"- change: {current.get('proposed_change', '').strip()}\n"
    )
    target.write_text(existing.rstrip() + block + "\n", encoding="utf-8")
    updated = proposals.apply_proposal(proposal_id, state_root=state_root)
    return {"ok": True, "proposal": updated, "target": str(target), "snapshot": snapshot}
