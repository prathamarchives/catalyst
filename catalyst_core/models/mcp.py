"""Structured MCP input/output models for Catalyst tools."""
from __future__ import annotations

from ._base import BaseModel, Field


class BrainContextInput(BaseModel):
    task: str
    project: str = "default"
    agent: str = "manual"


class EvaluateOutputInput(BaseModel):
    task: str
    output: str
    project: str = "default"


class CaptureFeedbackInput(BaseModel):
    task: str
    output: str = ""
    feedback: str
    project: str = "default"
    source: str = "user"


class ProposalListInput(BaseModel):
    project: str = "default"
    limit: int = 10
    status: str = "pending"


class ApplyProposalInput(BaseModel):
    proposal_id: str
    project: str = "default"
    approve: bool = True


class ToolResult(BaseModel):
    ok: bool = True
    data: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)

