"""Vector adapter boundary with deterministic no-dependency fallback."""
from __future__ import annotations

from collections import Counter
import math


class DeterministicVectorStore:
    """Tiny lexical-vector fallback for tests and fresh checkouts.

    Hosted or optional local vector backends can implement the same `similarity`
    contract later without changing kernel callers.
    """

    def similarity(self, query: str, text: str) -> float:
        a = _bag(query)
        b = _bag(text)
        if not a or not b:
            return 0.0
        dot = sum(a[k] * b.get(k, 0) for k in a)
        an = math.sqrt(sum(v * v for v in a.values()))
        bn = math.sqrt(sum(v * v for v in b.values()))
        if not an or not bn:
            return 0.0
        return dot / (an * bn)


def _bag(text: str) -> Counter:
    tokens = []
    token = ""
    for ch in (text or "").lower():
        if ch.isalnum():
            token += ch
        elif token:
            if len(token) > 2:
                tokens.append(token)
            token = ""
    if token and len(token) > 2:
        tokens.append(token)
    return Counter(tokens)

