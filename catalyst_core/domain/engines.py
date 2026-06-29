from __future__ import annotations

from typing import Any

from .base import BaseModel, Field


class EngineSpec(BaseModel):
    id: str = ""
    name: str = ""
    purpose: str = ""
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    mutation_rules: list[str] = Field(default_factory=list)
    eval_hooks: list[str] = Field(default_factory=list)
    health_metrics: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    confidence_behavior: str = ""


class EngineInput(BaseModel):
    engine_id: str = ""
    project: str = "default"
    input_ids: list[str] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)


class EngineRunRecord(BaseModel):
    id: str = ""
    engine_id: str = ""
    project: str = "default"
    status: str = "ok"
    input_ids: list[str] = Field(default_factory=list)
    proposed_mutation_ids: list[str] = Field(default_factory=list)
    committed_event_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

