"""Engine runtime: engines propose mutations, the kernel commits them."""
from __future__ import annotations

from typing import Protocol

from catalyst_core.domain.base import new_id, now_iso
from catalyst_core.domain.engines import EngineInput, EngineRunRecord, EngineSpec
from catalyst_core.domain.mutations import ProposedMutation

from .mutation_runtime import MutationRuntime


class CoreEngine(Protocol):
    spec: EngineSpec

    def run(self, engine_input: EngineInput) -> list[ProposedMutation]:
        ...


class EngineRuntime:
    def __init__(self, mutations: MutationRuntime):
        self.mutations = mutations

    def run(self, engine: CoreEngine, engine_input: EngineInput, commit: bool = True) -> dict:
        started = now_iso()
        proposed = engine.run(engine_input)
        if not commit:
            return {
                "engine_id": engine.spec.id,
                "proposed_mutations": [p.model_dump() for p in proposed],
                "committed_event_ids": [],
            }
        committed = self.mutations.commit(proposed) if proposed else None
        record = EngineRunRecord(
            id=new_id("engrun"),
            engine_id=engine.spec.id,
            project=engine_input.project,
            status="ok",
            input_ids=engine_input.input_ids,
            proposed_mutation_ids=[p.id for p in proposed],
            committed_event_ids=committed.event_ids if committed else [],
            warnings=[],
            started_at=started,
            finished_at=now_iso(),
            metadata={"mutation_count": len(proposed)},
        )
        run_mutation = ProposedMutation(
            id=new_id("mut"),
            type="engine_run.record",
            event_type="engine.ran",
            project=engine_input.project,
            aggregate_id=record.id,
            aggregate_type="engine_run",
            payload=record.model_dump(),
            engine_id=engine.spec.id,
        )
        run_commit = self.mutations.commit([run_mutation])
        return {
            "engine_id": engine.spec.id,
            "engine_run": record.model_dump(),
            "proposed_mutations": [p.model_dump() for p in proposed],
            "committed_event_ids": (committed.event_ids if committed else []) + run_commit.event_ids,
        }

