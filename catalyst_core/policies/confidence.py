"""Confidence update policy."""
from __future__ import annotations


def confidence_from_evidence(source_strength: float, confirmations: int = 0, contradictions: int = 0) -> float:
    score = 0.35 + (source_strength * 0.35) + min(confirmations, 5) * 0.08 - min(contradictions, 5) * 0.12
    return max(0.0, min(1.0, round(score, 4)))


def reinforce(confidence: float, amount: float = 0.08) -> float:
    return max(0.0, min(1.0, confidence + amount))


def weaken(confidence: float, amount: float = 0.12) -> float:
    return max(0.0, min(1.0, confidence - amount))

