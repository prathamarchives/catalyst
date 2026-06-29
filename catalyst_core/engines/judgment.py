from __future__ import annotations

from .base import BaseEngine
from .specs import ENGINE_SPECS


class JudgmentModelingEngine(BaseEngine):
    spec = next(s for s in ENGINE_SPECS if s.id == "judgment_engine")

