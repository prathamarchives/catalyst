"""Lightweight local retrieval for brain sections and memory atoms."""
from __future__ import annotations

import re
from pathlib import Path

from . import brain_manager, memory, store


def tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9][a-z0-9_-]{2,}", (text or "").lower())}


def score_text(query: str, text: str, boost: float = 0.0) -> float:
    q = tokenize(query)
    if not q:
        return boost
    hay = tokenize(text)
    if not hay:
        return 0.0
    return len(q & hay) / max(1, len(q)) + boost


def retrieve_memory_atoms(query: str, project: str | None = None, limit: int = 12,
                          state_root: Path = store.STATE_ROOT) -> list[dict]:
    rows = memory.list_memories(project=project, limit=1000, state_root=state_root)
    scored = []
    for row in rows:
        boost = 0.25 if row.get("target_brain") in {"judgment", "standards", "taste", "feedback"} else 0.0
        score = score_text(query, " ".join(str(row.get(k, "")) for k in ("text", "type", "target_brain")), boost)
        if score > 0:
            scored.append((score, row))
    return [dict(r, relevance=round(s, 3)) for s, r in sorted(scored, key=lambda x: (x[0], x[1].get("updated_at", "")), reverse=True)[:limit]]


def retrieve_brain_sections(query: str, project: str = "default", limit: int = 8,
                            outputs_root: Path | None = None) -> list[dict]:
    profile = brain_manager.load_brain_profile(project, outputs_root) if outputs_root else brain_manager.load_brain_profile(project)
    scored = []
    for name, section in profile.sections.items():
        boost = 0.2 if name in {"standards.md", "judgment.md", "rejected-examples.md", "taste.md"} else 0.0
        score = score_text(query, section.raw_markdown, boost)
        if score > 0:
            scored.append((score, section))
    return [
        {"name": s.name, "status": s.status, "relevance": round(score, 3), "summary": s.title}
        for score, s in sorted(scored, key=lambda x: x[0], reverse=True)[:limit]
    ]
