from __future__ import annotations

from catalyst_core.domain.engines import EngineInput, EngineSpec
from catalyst_core.domain.mutations import ProposedMutation


class BaseEngine:
    spec = EngineSpec()

    def run(self, engine_input: EngineInput) -> list[ProposedMutation]:
        return []

