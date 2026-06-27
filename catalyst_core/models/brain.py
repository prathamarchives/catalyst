"""Structured Catalyst Brain models."""
from __future__ import annotations

from typing import Any, Literal

from ._base import BaseModel, Field


class ContextSource(BaseModel):
    id: str = ""
    path: str = ""
    kind: str = "markdown"
    excerpt: str = ""
    trust: float = 0.5
    metadata: dict[str, Any] = Field(default_factory=dict)


class Standard(BaseModel):
    id: str = ""
    text: str = ""
    evidence: str = ""
    confidence: float = 0.5
    source_ids: list[str] = Field(default_factory=list)


class JudgmentRule(BaseModel):
    id: str = ""
    text: str = ""
    decision: str = ""
    evidence: str = ""
    confidence: float = 0.5
    source_ids: list[str] = Field(default_factory=list)


class RejectedPattern(BaseModel):
    id: str = ""
    pattern: str = ""
    reason: str = ""
    evidence: str = ""
    confidence: float = 0.5


class ApprovedExample(BaseModel):
    id: str = ""
    summary: str = ""
    evidence: str = ""
    why_it_works: str = ""
    confidence: float = 0.5


class FeedbackMemory(BaseModel):
    id: str = ""
    text: str = ""
    feedback_type: str = ""
    target_sections: list[str] = Field(default_factory=list)
    evidence: str = ""
    confidence: float = 0.5


class TaskPattern(BaseModel):
    id: str = ""
    task_type: str = ""
    rule: str = ""
    evidence: str = ""
    confidence: float = 0.5


class DecisionRule(BaseModel):
    id: str = ""
    if_then: str = ""
    applies_to: list[str] = Field(default_factory=list)
    evidence: str = ""
    confidence: float = 0.5


class BrainSection(BaseModel):
    name: str
    title: str = ""
    path: str = ""
    status: Literal["missing", "placeholder", "active"] = "missing"
    raw_markdown: str = ""
    unknown_markdown: str = ""
    standards: list[Standard] = Field(default_factory=list)
    judgment_rules: list[JudgmentRule] = Field(default_factory=list)
    rejected_patterns: list[RejectedPattern] = Field(default_factory=list)
    approved_examples: list[ApprovedExample] = Field(default_factory=list)
    feedback_memories: list[FeedbackMemory] = Field(default_factory=list)
    task_patterns: list[TaskPattern] = Field(default_factory=list)
    decision_rules: list[DecisionRule] = Field(default_factory=list)
    context_sources: list[ContextSource] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class BrainProfile(BaseModel):
    project: str = "default"
    sections: dict[str, BrainSection] = Field(default_factory=dict)
    standards: list[Standard] = Field(default_factory=list)
    judgment_rules: list[JudgmentRule] = Field(default_factory=list)
    rejected_patterns: list[RejectedPattern] = Field(default_factory=list)
    approved_examples: list[ApprovedExample] = Field(default_factory=list)
    feedback_memories: list[FeedbackMemory] = Field(default_factory=list)
    task_patterns: list[TaskPattern] = Field(default_factory=list)
    decision_rules: list[DecisionRule] = Field(default_factory=list)
    context_sources: list[ContextSource] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    placeholder_sections: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

