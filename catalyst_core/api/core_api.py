"""Core-only Python service boundary.

This module is the public Layer 2 API. It is intentionally not HTTP-first and
contains no UI, CLI, MCP, or onboarding assumptions.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from catalyst_core.domain.base import new_id
from catalyst_core.domain.engines import EngineInput
from catalyst_core.domain.retrieval import RetrievalQuery
from catalyst_core.engines import ENGINE_SPECS, EvidenceNormalizationEngine, FeedbackLearningEngine
from catalyst_core.kernel.cognitive_graph import CognitiveGraph
from catalyst_core.kernel.consolidation_runtime import ConsolidationRuntime
from catalyst_core.kernel.contradiction_runtime import ContradictionRuntime
from catalyst_core.kernel.engine_runtime import EngineRuntime
from catalyst_core.kernel.eval_runtime import EvalRuntime
from catalyst_core.kernel.event_log import EventLog
from catalyst_core.kernel.feedback_learner import FeedbackLearner
from catalyst_core.kernel.mutation_runtime import MutationRuntime
from catalyst_core.kernel.packet_compiler import PacketCompiler
from catalyst_core.kernel.retrieval_planner import RetrievalPlanner
from catalyst_core.storage.sqlite_store import SQLiteStore


class CatalystCore:
    def __init__(self, db_path: str | Path | None = None):
        self.store = SQLiteStore(db_path)
        self.mutations = MutationRuntime(self.store)
        self.events = EventLog(self.store)
        self.engine_runtime = EngineRuntime(self.mutations)
        self.graph_runtime = CognitiveGraph(self.store)
        self.retrieval_runtime = RetrievalPlanner(self.store, self.mutations)
        self.packet_runtime = PacketCompiler(self.store, self.mutations)
        self.eval_runtime = EvalRuntime(self.store, self.mutations)
        self.feedback_runtime = FeedbackLearner(self.store, self.mutations)
        self.consolidation_runtime = ConsolidationRuntime(self.store, self.mutations)
        self.contradiction_runtime = ContradictionRuntime(self.store, self.mutations)
        self._engines = {
            "evidence_engine": EvidenceNormalizationEngine(),
            "eval_feedback_engine": FeedbackLearningEngine(),
        }

    def ingest_evidence(self, content: str, project: str = "default", source: str = "manual",
                        source_type: str = "text", scope: str = "", audience: str = "",
                        task_type: str = "", metadata: dict[str, Any] | None = None) -> dict:
        engine = self._engines["evidence_engine"]
        engine_input = EngineInput(
            engine_id=engine.spec.id,
            project=project,
            data={
                "id": new_id("ev"),
                "content": content,
                "source": source,
                "source_type": source_type,
                "scope": scope,
                "audience": audience,
                "task_type": task_type,
                "metadata": metadata or {},
            },
        )
        run = self.engine_runtime.run(engine, engine_input)
        evidence = [
            m["payload"]
            for m in run["proposed_mutations"]
            if m.get("type") == "evidence.upsert"
        ][0]
        return {"evidence": evidence, "engine_run": run}

    def run_engine(self, engine_id: str, data: dict[str, Any], project: str = "default",
                   commit: bool = True) -> dict:
        if engine_id not in self._engines:
            raise ValueError(f"engine is not directly runnable yet: {engine_id}")
        return self.engine_runtime.run(
            self._engines[engine_id],
            EngineInput(engine_id=engine_id, project=project, data=data),
            commit=commit,
        )

    def run_pipeline(self, evidence: str, project: str = "default", **metadata) -> dict:
        return self.ingest_evidence(evidence, project=project, metadata=metadata)

    def retrieve_for_task(self, task: str, project: str = "default", task_type: str = "",
                          audience: str = "", scope: str = "", limit: int = 12) -> dict:
        return self.retrieval_runtime.retrieve(RetrievalQuery(
            task=task,
            project=project,
            task_type=task_type,
            audience=audience,
            scope=scope,
            limit=limit,
        ))

    def compile_packet(self, task: str, project: str = "default", task_type: str = "",
                       audience: str = "", scope: str = "", limit: int = 12) -> dict:
        return self.packet_runtime.compile(task, project, task_type, audience, scope, limit)

    def evaluate_output(self, packet_id: str, output: str, project: str = "default") -> dict:
        return self.eval_runtime.evaluate(packet_id, output, project)

    def receive_feedback(self, packet_id: str, output: str, feedback: str, project: str = "default",
                         feedback_type: str = "rejection") -> dict:
        return self.feedback_runtime.receive(packet_id, output, feedback, project, feedback_type)

    def consolidate_project(self, project: str = "default") -> dict:
        return self.consolidation_runtime.consolidate(project)

    def get_graph(self, project: str = "default") -> dict:
        return self.graph_runtime.graph(project)

    def get_health(self, project: str = "default") -> dict:
        objects = self.store.list_objects(project, status=None)
        edges = self.store.list_edges(project)
        packets = self.store.list_packets(project, 10000)
        proofs = self.store.list_proofs(project, 10000)
        events = self.store.get_event_count(project)
        by_type: dict[str, int] = {}
        by_memory: dict[str, int] = {}
        for obj in objects:
            by_type[obj["type"]] = by_type.get(obj["type"], 0) + 1
            fam = obj.get("memory_family") or "none"
            by_memory[fam] = by_memory.get(fam, 0) + 1
        return {
            "project": project,
            "event_count": events,
            "object_count": len(objects),
            "edge_count": len(edges),
            "packet_count": len(packets),
            "proof_count": len(proofs),
            "engine_count": len(ENGINE_SPECS),
            "by_type": by_type,
            "by_memory_family": by_memory,
            "canonical_store": "sqlite",
            "headless": True,
        }

    def export_state(self, project: str = "default") -> dict:
        return self.store.export_state(project)

    def engine_specs(self) -> list[dict]:
        return [s.model_dump() for s in ENGINE_SPECS]

