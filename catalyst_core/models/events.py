"""Structured runtime event, signal, memory, and proposal models."""
from __future__ import annotations

from typing import Any, Literal

from ._base import BaseModel, Field


class Event(BaseModel):
    id: str = ""
    type: str = "user_statement"
    project: str = "default"
    agent: str = "unknown"
    task: str = ""
    input: str = ""
    output: str = ""
    user_feedback: str = ""
    outcome: str = ""
    created_at: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class Signal(BaseModel):
    id: str = ""
    source_event_id: str = ""
    project: str = "default"
    type: str = "context_signal"
    text: str = ""
    confidence: float = 0.5
    target_brain: str = "context"
    status: Literal["candidate", "accepted", "rejected"] = "candidate"
    created_at: str = ""


class MemoryAtom(BaseModel):
    id: str = ""
    type: str = "fact"
    text: str = ""
    source_signal_ids: list[str] = Field(default_factory=list)
    source_event_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    maturity: int = 1
    status: str = "active"
    project: str = "default"
    target_brain: str = "context"
    created_at: str = ""
    updated_at: str = ""


class UpdateProposal(BaseModel):
    id: str = ""
    project: str = "default"
    target_file: str = ""
    target_brain: str = ""
    source_memory_id: str = ""
    source_event_id: str = ""
    proposed_change: str = ""
    reason: str = ""
    status: Literal["pending", "applied", "rejected", "blocked"] = "pending"
    confidence: float = 0.5
    created_at: str = ""
    updated_at: str = ""

