from __future__ import annotations

from .base import BaseEngine
from .specs import ENGINE_SPECS


class ContradictionScopeEngine(BaseEngine):
    spec = next(s for s in ENGINE_SPECS if s.id == "contradiction_scope_engine")

