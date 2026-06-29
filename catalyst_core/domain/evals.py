from __future__ import annotations

from typing import Any

from .base import BaseModel, Field


class EvalCheck(BaseModel):
    id: str = ""
    project: str = "default"
    object_id: str = ""
    name: str = ""
    check_type: str = "text_rule"
    content: str = ""
    failure_terms: list[str] = Field(default_factory=list)
    severity: str = "medium"
    created_at: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalResult(BaseModel):
    id: str = ""
    project: str = "default"
    packet_id: str = ""
    task: str = ""
    output: str = ""
    verdict: str = "ask"
    score: float = 0.0
    passed_check_ids: list[str] = Field(default_factory=list)
    failed_check_ids: list[str] = Field(default_factory=list)
    violated_object_ids: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    created_at: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

