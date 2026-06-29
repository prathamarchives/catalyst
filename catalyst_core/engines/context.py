from __future__ import annotations

from .base import BaseEngine
from .specs import ENGINE_SPECS


class ContextStateEngine(BaseEngine):
    spec = next(s for s in ENGINE_SPECS if s.id == "context_engine")

