"""Retrieval scoring policy."""
from __future__ import annotations


def total_score(parts: dict[str, float]) -> float:
    positive = (
        parts.get("semantic_similarity", 0.0)
        + parts.get("lexical_match", 0.0)
        + parts.get("graph_relevance", 0.0)
        + parts.get("scope_match", 0.0)
        + parts.get("audience_match", 0.0)
        + parts.get("confidence", 0.0)
        + parts.get("source_strength", 0.0)
        + parts.get("past_success", 0.0)
        + parts.get("eval_relevance", 0.0)
    )
    negative = (
        parts.get("stale_penalty", 0.0)
        + parts.get("contradiction_penalty", 0.0)
        + parts.get("overuse_penalty", 0.0)
    )
    return round(positive - negative, 6)


def lexical_overlap(query: str, text: str) -> float:
    q = set(tokens(query))
    t = set(tokens(text))
    if not q or not t:
        return 0.0
    return len(q & t) / max(1, len(q))


def tokens(text: str) -> list[str]:
    out: list[str] = []
    token = ""
    for ch in (text or "").lower():
        if ch.isalnum():
            token += ch
        elif token:
            if len(token) > 2:
                out.append(token)
            token = ""
    if token and len(token) > 2:
        out.append(token)
    return out

