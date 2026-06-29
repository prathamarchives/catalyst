"""Hybrid retrieval planner."""
from __future__ import annotations

from catalyst_core.domain.base import new_id, now_iso
from catalyst_core.domain.graph import ObjectEdge
from catalyst_core.domain.mutations import ProposedMutation
from catalyst_core.domain.retrieval import RetrievalCandidate, RetrievalQuery, RetrievalRunRecord
from catalyst_core.policies.contradiction import contradiction_penalty, scope_match
from catalyst_core.policies.decay import stale_penalty
from catalyst_core.policies.retrieval import lexical_overlap, tokens, total_score
from catalyst_core.storage.graph_store import GraphStore
from catalyst_core.storage.sqlite_store import SQLiteStore
from catalyst_core.storage.vector_store import DeterministicVectorStore

from .mutation_runtime import MutationRuntime


class RetrievalPlanner:
    def __init__(self, store: SQLiteStore, mutations: MutationRuntime):
        self.store = store
        self.mutations = mutations
        self.graph = GraphStore(store)
        self.vectors = DeterministicVectorStore()

    def retrieve(self, query: RetrievalQuery) -> dict:
        objects = self.store.list_objects(query.project, status="active")
        edges = self.store.list_edges(query.project)
        fts_hits = {r["object_id"]: abs(float(r.get("rank") or 0.0)) for r in self.store.search_fts(query.project, query.task, 50)}
        qtokens = set(tokens(query.task))
        candidates: list[RetrievalCandidate] = []
        excluded: list[dict] = []
        for obj in objects:
            content = obj.get("content") or ""
            lexical = lexical_overlap(query.task, content)
            if obj["id"] in fts_hits:
                lexical = max(lexical, 0.35)
            semantic = self.vectors.similarity(query.task, content)
            graph_score = min(0.25, self.graph.degree(query.project, obj["id"]) * 0.035)
            scope_score = scope_match(query.scope or query.task_type or query.task, obj.get("scope") or obj.get("task_type") or "")
            audience_score = 0.15 if query.audience and query.audience.lower() in (obj.get("audience") or "").lower() else 0.0
            confidence = float(obj.get("confidence") or 0.0) * 0.2
            source_strength = float(obj.get("source_strength") or 0.0) * 0.15
            past_success = (int(obj.get("success_count") or 0) - int(obj.get("failure_count") or 0)) * 0.05
            eval_relevance = 0.18 if obj.get("type") in {"eval_check", "anti_pattern", "standard_atom", "judgment_atom"} else 0.0
            if obj.get("type") == "anti_pattern" and (qtokens & set(tokens(content))):
                eval_relevance += 0.18
            parts = {
                "semantic_similarity": semantic,
                "lexical_match": lexical,
                "graph_relevance": graph_score,
                "scope_match": scope_score,
                "audience_match": audience_score,
                "confidence": confidence,
                "source_strength": source_strength,
                "past_success": past_success,
                "eval_relevance": eval_relevance,
                "stale_penalty": stale_penalty(obj.get("updated_at") or obj.get("created_at") or ""),
                "contradiction_penalty": contradiction_penalty(obj, edges),
                "overuse_penalty": min(0.2, int(obj.get("usage_count") or 0) * 0.015),
            }
            score = total_score(parts)
            trace = {
                "matched_task_terms": sorted(qtokens & set(tokens(content))),
                "evidence_ids": obj.get("evidence_ids") or [],
                "object_type": obj.get("type"),
                "why": _why(obj, parts),
            }
            candidate = RetrievalCandidate(
                object_id=obj["id"],
                object_type=obj.get("type") or "",
                content=content,
                score=score,
                breakdown=parts,
                trace=trace,
            )
            if score > 0.2:
                candidates.append(candidate)
            else:
                excluded.append({"object_id": obj["id"], "score": score, "reason": "below retrieval threshold"})
        candidates.sort(key=lambda c: c.score, reverse=True)
        selected = candidates[: max(1, min(query.limit or 12, 30))]
        run = RetrievalRunRecord(
            id=new_id("ret"),
            project=query.project,
            task=query.task,
            query=query.model_dump(),
            candidates=[c.model_dump() for c in candidates],
            selected_object_ids=[c.object_id for c in selected],
            excluded=excluded[:25],
            created_at=now_iso(),
        )
        mutations: list[ProposedMutation] = [
            ProposedMutation(
                id=new_id("mut"),
                type="retrieval.record",
                event_type="retrieval.ran",
                project=query.project,
                aggregate_id=run.id,
                aggregate_type="retrieval_run",
                payload=run.model_dump(),
                engine_id="retrieval_engine",
            )
        ]
        for cand in selected:
            edge = ObjectEdge(
                id=new_id("edge"),
                project=query.project,
                from_id=cand.object_id,
                to_id=run.id,
                type="retrieved_for",
                confidence=min(1.0, max(0.1, cand.score)),
                created_at=now_iso(),
                metadata={"task": query.task, "score": cand.score},
            )
            mutations.append(
                ProposedMutation(
                    id=new_id("mut"),
                    type="edge.create",
                    event_type="edge.created",
                    project=query.project,
                    aggregate_id=edge.id,
                    aggregate_type="object_edge",
                    payload=edge.model_dump(),
                    engine_id="retrieval_engine",
                )
            )
        self.mutations.commit(mutations)
        return {"run": run.model_dump(), "candidates": [c.model_dump() for c in selected], "excluded": excluded[:25]}


def _why(obj: dict, parts: dict[str, float]) -> str:
    reasons = []
    if parts.get("lexical_match", 0) > 0.2:
        reasons.append("lexical task match")
    if parts.get("semantic_similarity", 0) > 0.2:
        reasons.append("semantic similarity")
    if parts.get("eval_relevance", 0) > 0.0:
        reasons.append("eval/negative constraint relevance")
    if parts.get("graph_relevance", 0) > 0.0:
        reasons.append("graph-connected")
    if not reasons:
        reasons.append(f"{obj.get('type')} above score threshold")
    return ", ".join(reasons)

