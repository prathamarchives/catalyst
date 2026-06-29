from __future__ import annotations

from .base import BaseModel


class MemoryAssignment(BaseModel):
    object_id: str = ""
    family: str = "semantic"
    reason: str = ""

