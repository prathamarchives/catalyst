"""Consolidation policy."""
from __future__ import annotations

from .retrieval import tokens


def cluster_key(text: str) -> str:
    important = [t for t in tokens(text) if t not in {"this", "that", "with", "from", "avoid", "never"}]
    return " ".join(sorted(set(important))[:8])


def should_consolidate(objects: list[dict], min_support: int = 2) -> bool:
    return len(objects) >= min_support

