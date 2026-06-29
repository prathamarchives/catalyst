from __future__ import annotations

from typing import Any

from .base import BaseModel, Field


class RetrievalQuery(BaseModel):
    task: str = ""
    project: str = "default"
    task_type: str = ""
    audience: str = ""
    scope: str = ""
    limit: int = 12


class ScoreBreakdown(BaseModel):
    semantic_similarity: float = 0.0
    lexical_match: float = 0.0
    graph_relevance: float = 0.0
    scope_match: float = 0.0
    audience_match: float = 0.0
    confidence: float = 0.0
    source_strength: float = 0.0
    past_success: float = 0.0
    eval_relevance: float = 0.0
    stale_penalty: float = 0.0
    contradiction_penalty: float = 0.0
    overuse_penalty: float = 0.0


class RetrievalCandidate(BaseModel):
    object_id: str = ""
    object_type: str = ""
    content: str = ""
    score: float = 0.0
    breakdown: dict[str, float] = Field(default_factory=dict)
    trace: dict[str, Any] = Field(default_factory=dict)


class RetrievalRunRecord(BaseModel):
    id: str = ""
    project: str = "default"
    task: str = ""
    query: dict[str, Any] = Field(default_factory=dict)
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    selected_object_ids: list[str] = Field(default_factory=list)
    excluded: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str = ""

