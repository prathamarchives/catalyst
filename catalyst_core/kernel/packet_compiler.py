"""Task-specific agent packet compiler."""
from __future__ import annotations

from collections import defaultdict

from catalyst_core.domain.base import new_id, now_iso
from catalyst_core.domain.graph import ObjectEdge
from catalyst_core.domain.mutations import ProposedMutation
from catalyst_core.domain.objects import CognitiveObject
from catalyst_core.domain.packets import AgentPacket, PacketSection
from catalyst_core.domain.retrieval import RetrievalQuery
from catalyst_core.storage.sqlite_store import SQLiteStore

from .mutation_runtime import MutationRuntime
from .proof_runtime import ProofRuntime
from .retrieval_planner import RetrievalPlanner


class PacketCompiler:
    def __init__(self, store: SQLiteStore, mutations: MutationRuntime):
        self.store = store
        self.mutations = mutations
        self.retrieval = RetrievalPlanner(store, mutations)
        self.proofs = ProofRuntime(store, mutations)

    def compile(self, task: str, project: str = "default", task_type: str = "", audience: str = "",
                scope: str = "", limit: int = 12) -> dict:
        retrieval = self.retrieval.retrieve(RetrievalQuery(
            task=task,
            project=project,
            task_type=task_type,
            audience=audience,
            scope=scope,
            limit=limit,
        ))
        object_ids = [c["object_id"] for c in retrieval["candidates"]]
        objects = [self.store.get_object(oid) for oid in object_ids]
        objects = [o for o in objects if o]
        sections = _sections(objects)
        eval_check_ids = [o["id"] for o in objects if o.get("type") == "eval_check"]
        packet_text = _render_packet(task, sections, retrieval["candidates"])
        packet = AgentPacket(
            id=new_id("packet"),
            project=project,
            task=task,
            task_type=task_type,
            audience=audience,
            scope=scope,
            retrieval_run_id=retrieval["run"]["id"],
            object_ids=object_ids,
            eval_check_ids=eval_check_ids,
            sections=[s.model_dump() for s in sections],
            packet=packet_text,
            trace=[c["trace"] for c in retrieval["candidates"]],
            created_at=now_iso(),
        )
        packet_object = CognitiveObject(
            id=packet.id,
            type="agent_packet",
            content=packet_text,
            scope=scope,
            project=project,
            audience=audience,
            task_type=task_type,
            confidence=0.7 if object_ids else 0.25,
            source_strength=0.5,
            evidence_ids=[],
            status="active",
            created_at=packet.created_at,
            updated_at=packet.created_at,
            metadata={"task": task, "retrieval_run_id": packet.retrieval_run_id},
        )
        mutations: list[ProposedMutation] = [
            ProposedMutation(
                id=new_id("mut"),
                type="packet.record",
                event_type="packet.compiled",
                project=project,
                aggregate_id=packet.id,
                aggregate_type="agent_packet",
                payload=packet.model_dump(),
                engine_id="packet_engine",
            ),
            ProposedMutation(
                id=new_id("mut"),
                type="object.upsert",
                event_type="object.confirmed",
                project=project,
                aggregate_id=packet_object.id,
                aggregate_type="cognitive_object",
                payload=packet_object.model_dump(),
                engine_id="packet_engine",
            ),
        ]
        for oid in object_ids:
            edge = ObjectEdge(
                id=new_id("edge"),
                project=project,
                from_id=oid,
                to_id=packet.id,
                type="compiled_into",
                confidence=0.8,
                created_at=now_iso(),
                metadata={"task": task},
            )
            mutations.append(ProposedMutation(
                id=new_id("mut"),
                type="edge.create",
                event_type="edge.created",
                project=project,
                aggregate_id=edge.id,
                aggregate_type="object_edge",
                payload=edge.model_dump(),
                engine_id="packet_engine",
            ))
            mutations.append(ProposedMutation(
                id=new_id("mut"),
                type="object_score.update",
                event_type="retrieval_weight.updated",
                project=project,
                aggregate_id=oid,
                aggregate_type="object_score",
                payload={"object_id": oid, "project": project, "retrieval_weight_delta": 0.02, "mark_used": True},
                engine_id="packet_engine",
            ))
        self.mutations.commit(mutations)
        proof = self.proofs.link_latest_feedback_to_packet(project, packet.id, object_ids)
        return {"packet": packet.model_dump(), "retrieval": retrieval, "proof": proof}


def _sections(objects: list[dict]) -> list[PacketSection]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for obj in objects:
        groups[obj.get("type") or "memory_atom"].append(obj)
    order = [
        ("Active Context", ["context_atom", "identity_atom"]),
        ("Standards", ["standard_atom"]),
        ("Taste And Judgment", ["taste_delta", "judgment_atom", "memory_atom"]),
        ("Anti-Patterns", ["anti_pattern"]),
        ("References", ["reference_item"]),
        ("Eval Checks", ["eval_check"]),
    ]
    sections: list[PacketSection] = []
    for title, types in order:
        items = [o for typ in types for o in groups.get(typ, [])]
        if not items:
            continue
        lines = [f"- [{o['type']}] {o['content']}" for o in items[:5]]
        sections.append(PacketSection(title=title, object_ids=[o["id"] for o in items[:5]], content="\n".join(lines)))
    return sections


def _render_packet(task: str, sections: list[PacketSection], candidates: list[dict]) -> str:
    lines = [
        "# Catalyst Agent Packet",
        "",
        f"Task: {task}",
        "",
        "This is a task-specific operating brief. It is not a memory dump.",
    ]
    for section in sections:
        lines.extend(["", f"## {section.title}", section.content])
    lines.extend(["", "## Workflow", "- Use the standards and anti-patterns before drafting.", "- Run eval checks before treating output as acceptable."])
    lines.extend(["", "## Retrieval Trace"])
    for cand in candidates[:8]:
        lines.append(f"- {cand['object_id']}: {cand['trace'].get('why')} (score {cand['score']:.3f})")
    return "\n".join(lines).strip() + "\n"

