from __future__ import annotations

from typing import Any

from .base import BaseModel, Field


class EvidenceItem(BaseModel):
    id: str = ""
    project: str = "default"
    content: str = ""
    source: str = "manual"
    source_type: str = "text"
    scope: str = ""
    audience: str = ""
    task_type: str = ""
    artifact_id: str = ""
    source_strength: float = 0.6
    created_at: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

