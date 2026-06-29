from __future__ import annotations

from typing import Any

from .base import BaseModel, Field


class CognitiveObject(BaseModel):
    id: str = ""
    type: str = "memory_atom"
    content: str = ""
    scope: str = ""
    project: str = "default"
    audience: str = ""
    task_type: str = ""
    confidence: float = 0.5
    source_strength: float = 0.5
    evidence_ids: list[str] = Field(default_factory=list)
    version: int = 1
    status: str = "active"
    created_at: str = ""
    updated_at: str = ""
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    memory_family: str = ""
    parent_ids: list[str] = Field(default_factory=list)
    embedding_id: str = ""
    eval_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

