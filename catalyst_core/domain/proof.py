from __future__ import annotations

from typing import Any

from .base import BaseModel, Field


class ProofRecord(BaseModel):
    id: str = ""
    project: str = "default"
    before_packet_id: str = ""
    feedback_event_id: str = ""
    after_packet_id: str = ""
    eval_result_id: str = ""
    created_object_ids: list[str] = Field(default_factory=list)
    updated_object_ids: list[str] = Field(default_factory=list)
    claim: str = ""
    created_at: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

