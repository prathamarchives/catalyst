"""Feedback learner."""
from __future__ import annotations

from catalyst_core.domain.engines import EngineInput
from catalyst_core.engines.feedback import FeedbackLearningEngine
from catalyst_core.storage.sqlite_store import SQLiteStore

from .engine_runtime import EngineRuntime
from .mutation_runtime import MutationRuntime


class FeedbackLearner:
    def __init__(self, store: SQLiteStore, mutations: MutationRuntime):
        self.store = store
        self.mutations = mutations
        self.engine_runtime = EngineRuntime(mutations)
        self.engine = FeedbackLearningEngine()

    def receive(self, packet_id: str, output: str, feedback: str, project: str = "default",
                feedback_type: str = "rejection") -> dict:
        packet = self.store.get_packet(packet_id) if packet_id else None
        engine_input = EngineInput(
            engine_id=self.engine.spec.id,
            project=project,
            input_ids=[packet_id] if packet_id else [],
            data={
                "packet": packet or {},
                "packet_id": packet_id,
                "task": (packet or {}).get("task") or "",
                "output": output or "",
                "feedback": feedback or "",
                "feedback_type": feedback_type,
            },
        )
        run = self.engine_runtime.run(self.engine, engine_input, commit=True)
        created_object_ids = [
            m["payload"]["id"]
            for m in run["proposed_mutations"]
            if m.get("type") == "object.upsert"
        ]
        feedback_ids = [
            m["payload"]["id"]
            for m in run["proposed_mutations"]
            if m.get("type") == "feedback.record"
        ]
        return {
            "engine_run": run,
            "created_object_ids": created_object_ids,
            "feedback_event_id": feedback_ids[0] if feedback_ids else "",
        }

