"""Consolidation runtime."""
from __future__ import annotations

from collections import defaultdict

from catalyst_core.domain.base import new_id, now_iso
from catalyst_core.domain.graph import ObjectEdge
from catalyst_core.domain.mutations import ProposedMutation
from catalyst_core.domain.objects import CognitiveObject
from catalyst_core.policies.consolidation import cluster_key, should_consolidate
from catalyst_core.storage.sqlite_store import SQLiteStore

from .mutation_runtime import MutationRuntime


class ConsolidationRuntime:
    def __init__(self, store: SQLiteStore, mutations: MutationRuntime):
        self.store = store
        self.mutations = mutations

    def consolidate(self, project: str = "default") -> dict:
        objects = [o for o in self.store.list_objects(project) if o.get("type") in {"anti_pattern", "taste_delta", "judgment_atom"}]
        clusters: dict[str, list[dict]] = defaultdict(list)
        for obj in objects:
            clusters[cluster_key(obj.get("content") or "")].append(obj)
        created: list[str] = []
        mutations: list[ProposedMutation] = []
        for key, items in clusters.items():
            if not key or not should_consolidate(items):
                continue
            evidence_ids = sorted({eid for item in items for eid in (item.get("evidence_ids") or [])})
            consolidated = CognitiveObject(
                id=new_id("obj"),
                type="anti_pattern" if any(i.get("type") == "anti_pattern" for i in items) else "standard_atom",
                content=f"Consolidated rule from repeated signals: {items[0]['content']}",
                scope=items[0].get("scope") or "",
                project=project,
                audience=items[0].get("audience") or "",
                task_type=items[0].get("task_type") or "",
                confidence=min(0.95, max(float(i.get("confidence") or 0.5) for i in items) + 0.1),
                source_strength=max(float(i.get("source_strength") or 0.5) for i in items),
                evidence_ids=evidence_ids,
                status="consolidated",
                created_at=now_iso(),
                updated_at=now_iso(),
                metadata={"cluster_key": key, "source_object_ids": [i["id"] for i in items]},
            )
            created.append(consolidated.id)
            mutations.append(ProposedMutation(
                id=new_id("mut"),
                type="object.upsert",
                event_type="object.confirmed",
                project=project,
                aggregate_id=consolidated.id,
                aggregate_type="cognitive_object",
                payload=consolidated.model_dump(),
                engine_id="consolidation_engine",
            ))
            for item in items:
                edge = ObjectEdge(
                    id=new_id("edge"),
                    project=project,
                    from_id=item["id"],
                    to_id=consolidated.id,
                    type="consolidates",
                    confidence=0.9,
                    created_at=now_iso(),
                    metadata={"cluster_key": key},
                )
                mutations.append(ProposedMutation(
                    id=new_id("mut"),
                    type="edge.create",
                    event_type="edge.created",
                    project=project,
                    aggregate_id=edge.id,
                    aggregate_type="object_edge",
                    payload=edge.model_dump(),
                    engine_id="consolidation_engine",
                ))
        if mutations:
            self.mutations.commit(mutations)
        return {"created_object_ids": created, "cluster_count": len(created)}

