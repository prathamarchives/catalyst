"""Contradiction/scope policy."""
from __future__ import annotations


def contradiction_penalty(obj: dict, edges: list[dict]) -> float:
    if obj.get("status") == "contradicted":
        return 0.6
    oid = obj.get("id")
    if any(e.get("type") == "contradicts" and (e.get("from_id") == oid or e.get("to_id") == oid) for e in edges):
        return 0.25
    return 0.0


def scope_match(task_scope: str, object_scope: str) -> float:
    if not object_scope:
        return 0.08
    if not task_scope:
        return 0.04
    return 0.25 if object_scope.lower() in task_scope.lower() or task_scope.lower() in object_scope.lower() else 0.0

