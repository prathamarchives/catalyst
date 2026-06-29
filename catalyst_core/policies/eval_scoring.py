"""Eval scoring policy."""
from __future__ import annotations


def score_from_failures(total_checks: int, failed: int) -> float:
    if total_checks <= 0:
        return 0.0
    return max(0.0, round(1.0 - (failed / total_checks), 4))


def verdict(score: float, failed: int) -> str:
    if failed >= 2:
        return "reject"
    if failed == 1 or score < 0.75:
        return "revise"
    return "ship"

