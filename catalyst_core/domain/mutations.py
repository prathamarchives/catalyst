from __future__ import annotations

from typing import Any

from .base import BaseModel, Field


class ProposedMutation(BaseModel):
    id: str = ""
    type: str = ""
    event_type: str = ""
    project: str = "default"
    aggregate_id: str = ""
    aggregate_type: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    engine_id: str = ""
    idempotency_key: str = ""


class ValidationResult(BaseModel):
    ok: bool = True
    errors: list[str] = Field(default_factory=list)


class CommittedEvents(BaseModel):
    event_ids: list[str] = Field(default_factory=list)
    mutation_ids: list[str] = Field(default_factory=list)

