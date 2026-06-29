from __future__ import annotations

from typing import Any

from .base import BaseModel, Field


class CoreEvent(BaseModel):
    id: str = ""
    type: str = ""
    project: str = "default"
    aggregate_id: str = ""
    aggregate_type: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = ""
    created_at: str = ""

