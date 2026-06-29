"""Catalyst Core V1 object models.

Core V1 is object-first: markdown can still be exported for people, but the
mechanism stores evidence, memory, packets, evals, feedback, and proof as typed
local objects with graph links.
"""
from __future__ import annotations

from typing import Any, Literal

from ._base import BaseModel, Field

CoreStatus = Literal["candidate", "active", "consolidated", "stale", "contradicted", "archived", "low_confidence"]


class CoreObject(BaseModel):
    id: str = ""
    type: str = "memory_atom"
    title: str = ""
    content: str = ""
    summary: str = ""
    project: str = "default"
    task_type: str = ""
    audience: str = ""
    scope: str = ""
    confidence: float = 0.5
    source_strength: float = 0.5
    status: CoreStatus = "candidate"
    memory_type: str = ""
    engine_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    evidence_ids: list[str] = Field(default_factory=list)
    related_ids: list[str] = Field(default_factory=list)
    contradicts_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CoreEdge(BaseModel):
    id: str = ""
    from_id: str = ""
    to_id: str = ""
    type: str = "related_to"
    project: str = "default"
    engine_id: str = ""
    confidence: float = 0.7
    created_at: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class EngineSpec(BaseModel):
    id: str
    name: str
    purpose: str
    inputs: list[str]
    outputs: list[str]
    retrieval_role: str
    consolidation_role: str
    feedback_role: str
    eval_hooks: list[str]
    health_metrics: list[str]
    failure_modes: list[str]


class EngineRun(BaseModel):
    id: str = ""
    engine_id: str = ""
    project: str = "default"
    status: str = "ok"
    input_ids: list[str] = Field(default_factory=list)
    output_ids: list[str] = Field(default_factory=list)
    warning_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    created_at: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentPacket(BaseModel):
    id: str = ""
    task: str = ""
    project: str = "default"
    task_type: str = ""
    retrieval_set_id: str = ""
    object_ids: list[str] = Field(default_factory=list)
    packet: str = ""
    eval_check_ids: list[str] = Field(default_factory=list)
    trace: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    created_at: str = ""


class CoreEvalResult(BaseModel):
    id: str = ""
    packet_id: str = ""
    project: str = "default"
    task: str = ""
    output: str = ""
    verdict: Literal["ship", "revise", "reject", "ask"] = "ask"
    score: float = 0.0
    passed_check_ids: list[str] = Field(default_factory=list)
    failed_check_ids: list[str] = Field(default_factory=list)
    violated_object_ids: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    created_at: str = ""


class CoreHealth(BaseModel):
    project: str = "default"
    object_count: int = 0
    edge_count: int = 0
    evidence_count: int = 0
    memory_count: int = 0
    eval_count: int = 0
    packet_count: int = 0
    feedback_count: int = 0
    proof_count: int = 0
    engine_count: int = 0
    warning_count: int = 0
    unprocessed_evidence_count: int = 0
    orphan_object_count: int = 0
    low_confidence_count: int = 0
    stale_count: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)
    by_memory_type: dict[str, int] = Field(default_factory=dict)
    engine_health: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    created_at: str = ""
