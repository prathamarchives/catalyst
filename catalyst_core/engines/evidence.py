from __future__ import annotations

from catalyst_core.domain.base import new_id, now_iso
from catalyst_core.domain.engines import EngineInput
from catalyst_core.domain.evidence import EvidenceItem
from catalyst_core.domain.mutations import ProposedMutation

from .base import BaseEngine
from .specs import ENGINE_SPECS


class EvidenceNormalizationEngine(BaseEngine):
    spec = next(s for s in ENGINE_SPECS if s.id == "evidence_engine")

    def run(self, engine_input: EngineInput) -> list[ProposedMutation]:
        data = engine_input.data
        evidence = EvidenceItem(
            id=data.get("id") or new_id("ev"),
            project=engine_input.project,
            content=(data.get("content") or "").strip(),
            source=data.get("source") or "manual",
            source_type=data.get("source_type") or "text",
            scope=data.get("scope") or "",
            audience=data.get("audience") or "",
            task_type=data.get("task_type") or "",
            artifact_id=data.get("artifact_id") or "",
            source_strength=float(data.get("source_strength") or 0.6),
            created_at=now_iso(),
            metadata=data.get("metadata") or {},
        )
        return [
            ProposedMutation(
                id=new_id("mut"),
                type="evidence.upsert",
                event_type="evidence.ingested",
                project=engine_input.project,
                aggregate_id=evidence.id,
                aggregate_type="evidence_item",
                payload=evidence.model_dump(),
                engine_id=self.spec.id,
            )
        ]

