"""Structured evaluation and runtime health models."""
from __future__ import annotations

from typing import Any, Literal

from ._base import BaseModel, Field


class EvalIssue(BaseModel):
    id: str = ""
    severity: Literal["info", "warn", "block"] = "warn"
    dimension: str = ""
    message: str = ""
    evidence: str = ""
    suggested_fix: str = ""


class EvalResult(BaseModel):
    verdict: Literal["ship", "revise", "reject", "ask"] = "ask"
    scores: dict[str, float] = Field(default_factory=dict)
    issues: list[EvalIssue] = Field(default_factory=list)
    matched_rules: list[str] = Field(default_factory=list)
    violated_patterns: list[str] = Field(default_factory=list)
    suggested_feedback: list[str] = Field(default_factory=list)
    proposal_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuntimeHealth(BaseModel):
    ok: bool = True
    project: str = "all"
    events_count: int = 0
    signals_count: int = 0
    memories_count: int = 0
    graph_node_count: int = 0
    graph_edge_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    maturity: dict[str, Any] = Field(default_factory=dict)

