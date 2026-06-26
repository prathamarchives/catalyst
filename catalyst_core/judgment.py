"""Rule-based output review against recalled persona memories."""
from __future__ import annotations

from pathlib import Path

from . import memory, recall, store
from .evaluator import BUILTIN_SLOP


def review_output(task: str, output: str, project: str | None = None,
                  state_root: Path = store.STATE_ROOT) -> dict:
    packet = recall.build_context_packet(task, project=project, agent="judgment", state_root=state_root)
    out = (output or "").strip()
    low = out.lower()
    slop_hits = [s for s in BUILTIN_SLOP if s in low]
    rejection_memories = [
        m for m in memory.search_memories("reject never bad slop dislike", project=project, limit=50, state_root=state_root)
        if m.get("target_brain") in {"judgment", "feedback", "taste", "standards"}
    ]
    matched = [m for m in rejection_memories if any(w and w in low for w in (m.get("text") or "").lower().split()[:8])]
    failed = []
    if slop_hits:
        failed.append("generic/AI-tell phrases present: " + ", ".join(slop_hits[:5]))
    if matched:
        failed.append("matches known rejection/feedback memory")
    if not out:
        failed.append("empty output")
    score = max(0, 100 - len(slop_hits) * 15 - len(matched) * 20 - (40 if not out else 0))
    result = {
        "id": store.new_id("jr"),
        "task": task,
        "output_summary": out[:240],
        "score": score,
        "passes": score >= 75 and not failed,
        "failed_standards": failed,
        "matched_rejections": matched[:5],
        "recommended_revision": "Remove matched weak patterns and revise against selected standards." if failed else "",
        "source_context_packet_id": packet["id"],
        "source_memories": [m["id"] for m in packet.get("relevant_memories", [])],
        "created_at": store.now_iso(),
    }
    store.append_jsonl("logs/reviews.jsonl", result, state_root)
    return result

