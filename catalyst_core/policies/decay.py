"""Staleness policy."""
from __future__ import annotations

from datetime import datetime, timezone


def stale_penalty(updated_at: str, recently_used: bool = False) -> float:
    if recently_used:
        return 0.0
    try:
        clean = (updated_at or "").replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        age_days = max(0, (datetime.now(timezone.utc) - dt).days)
    except Exception:
        age_days = 0
    if age_days < 30:
        return 0.0
    return min(0.35, age_days / 365.0)

