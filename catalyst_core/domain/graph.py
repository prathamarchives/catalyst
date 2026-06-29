from __future__ import annotations

from typing import Any

from .base import BaseModel, Field


class ObjectEdge(BaseModel):
    id: str = ""
    project: str = "default"
    from_id: str = ""
    to_id: str = ""
    type: str = "supports"
    confidence: float = 0.7
    created_at: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphPath(BaseModel):
    start_id: str = ""
    end_id: str = ""
    edge_ids: list[str] = Field(default_factory=list)
    node_ids: list[str] = Field(default_factory=list)

