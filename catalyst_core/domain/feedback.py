from __future__ import annotations

from typing import Any

from .base import BaseModel, Field


class FeedbackEvent(BaseModel):
    id: str = ""
    project: str = "default"
    packet_id: str = ""
    eval_result_id: str = ""
    task: str = ""
    output: str = ""
    feedback: str = ""
    feedback_type: str = "rejection"
    created_at: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class LearningUpdate(BaseModel):
    object_id: str = ""
    confidence_delta: float = 0.0
    retrieval_weight_delta: float = 0.0
    reason: str = ""

