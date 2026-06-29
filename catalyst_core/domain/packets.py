from __future__ import annotations

from typing import Any

from .base import BaseModel, Field


class PacketSection(BaseModel):
    title: str = ""
    object_ids: list[str] = Field(default_factory=list)
    content: str = ""


class AgentPacket(BaseModel):
    id: str = ""
    project: str = "default"
    task: str = ""
    task_type: str = ""
    audience: str = ""
    scope: str = ""
    retrieval_run_id: str = ""
    object_ids: list[str] = Field(default_factory=list)
    eval_check_ids: list[str] = Field(default_factory=list)
    sections: list[dict[str, Any]] = Field(default_factory=list)
    packet: str = ""
    trace: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str = ""

