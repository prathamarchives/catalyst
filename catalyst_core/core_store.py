"""Local object store for Catalyst Core V1.

Append-only JSONL keeps the store easy to inspect, diff, and recover. Latest
record per id wins for queries; provenance stays in the log.
"""
from __future__ import annotations

from pathlib import Path

from . import store
from .models.core import AgentPacket, CoreEdge, CoreEvalResult, CoreHealth, CoreObject, EngineRun

OBJECTS_REL = "core/objects.jsonl"
EDGES_REL = "core/edges.jsonl"
ENGINE_RUNS_REL = "core/engine-runs.jsonl"
PACKETS_REL = "core/packets.jsonl"
EVALS_REL = "core/evals.jsonl"
PROOFS_REL = "core/proofs.jsonl"

MEMORY_OBJECT_TYPES = {
    "memory_atom",
    "identity_atom",
    "context_atom",
    "taste_delta",
    "taste_rule",
    "judgment_atom",
    "standard_atom",
    "anti_pattern",
    "reference_item",
    "eval_check",
}


def _latest_by_id(rows: list[dict]) -> list[dict]:
    latest: dict[str, dict] = {}
    for row in rows:
        rid = row.get("id")
        if rid:
            latest[rid] = row
    return sorted(latest.values(), key=lambda r: r.get("updated_at") or r.get("created_at") or "", reverse=True)


def save_object(obj: CoreObject | dict, state_root: Path = store.STATE_ROOT) -> dict:
    data = obj.model_dump() if hasattr(obj, "model_dump") else dict(obj)
    now = store.now_iso()
    data.setdefault("id", store.new_id("obj"))
    data.setdefault("created_at", now)
    data["updated_at"] = now
    return store.append_jsonl(OBJECTS_REL, data, state_root)


def get_object(object_id: str, state_root: Path = store.STATE_ROOT) -> dict | None:
    for row in _latest_by_id(store.read_jsonl(OBJECTS_REL, state_root)):
        if row.get("id") == object_id:
            return row
    return None


def list_objects(project: str | None = None, type: str | None = None, status: str | None = None,
                 state_root: Path = store.STATE_ROOT, limit: int = 1000) -> list[dict]:
    rows = _latest_by_id(store.read_jsonl(OBJECTS_REL, state_root))
    if project:
        rows = [r for r in rows if (r.get("project") or "default") == project]
    if type:
        rows = [r for r in rows if r.get("type") == type]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    return rows[: max(1, min(10000, int(limit or 1000)))]


def add_edge(from_id: str, to_id: str, type: str, project: str = "default",
             engine_id: str = "", confidence: float = 0.7,
             metadata: dict | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    edge = CoreEdge(
        id=store.new_id("edge"),
        from_id=from_id,
        to_id=to_id,
        type=type,
        project=project,
        engine_id=engine_id,
        confidence=confidence,
        created_at=store.now_iso(),
        metadata=metadata or {},
    )
    return store.append_jsonl(EDGES_REL, edge.model_dump(), state_root)


def list_edges(project: str | None = None, state_root: Path = store.STATE_ROOT) -> list[dict]:
    rows = store.read_jsonl(EDGES_REL, state_root)
    if project:
        rows = [r for r in rows if (r.get("project") or "default") == project]
    return rows


def save_engine_run(run: EngineRun | dict, state_root: Path = store.STATE_ROOT) -> dict:
    data = run.model_dump() if hasattr(run, "model_dump") else dict(run)
    data.setdefault("id", store.new_id("engrun"))
    data.setdefault("created_at", store.now_iso())
    return store.append_jsonl(ENGINE_RUNS_REL, data, state_root)


def list_engine_runs(project: str | None = None, state_root: Path = store.STATE_ROOT) -> list[dict]:
    rows = store.read_jsonl(ENGINE_RUNS_REL, state_root)
    if project:
        rows = [r for r in rows if (r.get("project") or "default") == project]
    return store.latest(rows, 1000)


def save_packet(packet: AgentPacket | dict, state_root: Path = store.STATE_ROOT) -> dict:
    data = packet.model_dump() if hasattr(packet, "model_dump") else dict(packet)
    data.setdefault("id", store.new_id("packet"))
    data.setdefault("created_at", store.now_iso())
    return store.append_jsonl(PACKETS_REL, data, state_root)


def list_packets(project: str | None = None, state_root: Path = store.STATE_ROOT) -> list[dict]:
    rows = store.read_jsonl(PACKETS_REL, state_root)
    if project:
        rows = [r for r in rows if (r.get("project") or "default") == project]
    return store.latest(rows, 200)


def save_eval(result: CoreEvalResult | dict, state_root: Path = store.STATE_ROOT) -> dict:
    data = result.model_dump() if hasattr(result, "model_dump") else dict(result)
    data.setdefault("id", store.new_id("eval"))
    data.setdefault("created_at", store.now_iso())
    return store.append_jsonl(EVALS_REL, data, state_root)


def list_evals(project: str | None = None, state_root: Path = store.STATE_ROOT) -> list[dict]:
    rows = store.read_jsonl(EVALS_REL, state_root)
    if project:
        rows = [r for r in rows if (r.get("project") or "default") == project]
    return store.latest(rows, 200)


def save_proof(proof: dict, state_root: Path = store.STATE_ROOT) -> dict:
    payload = {
        "id": proof.get("id") or store.new_id("proof"),
        "project": proof.get("project") or "default",
        "packet_id": proof.get("packet_id") or "",
        "before": proof.get("before") or "",
        "after": proof.get("after") or "",
        "feedback": proof.get("feedback") or "",
        "object_ids": proof.get("object_ids") or [],
        "created_at": proof.get("created_at") or store.now_iso(),
        "metadata": proof.get("metadata") or {},
    }
    return store.append_jsonl(PROOFS_REL, payload, state_root)


def list_proofs(project: str | None = None, state_root: Path = store.STATE_ROOT) -> list[dict]:
    rows = store.read_jsonl(PROOFS_REL, state_root)
    if project:
        rows = [r for r in rows if (r.get("project") or "default") == project]
    return store.latest(rows, 200)


def graph(project: str | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    objects = list_objects(project=project, state_root=state_root, limit=10000)
    packets = list_packets(project=project, state_root=state_root)
    evals = list_evals(project=project, state_root=state_root)
    proofs = list_proofs(project=project, state_root=state_root)
    nodes = [
        {
            "id": o["id"],
            "kind": o.get("type"),
            "label": o.get("title") or o.get("summary") or o.get("type"),
            "status": o.get("status"),
            "confidence": o.get("confidence"),
            "memory_type": o.get("memory_type"),
        }
        for o in objects
    ]
    nodes.extend({"id": p["id"], "kind": "agent_packet", "label": p.get("task"), "status": "active"} for p in packets)
    nodes.extend({"id": e["id"], "kind": "eval_result", "label": e.get("verdict"), "status": e.get("verdict")} for e in evals)
    nodes.extend({"id": p["id"], "kind": "proof_record", "label": "before/after proof", "status": "active"} for p in proofs)
    return {
        "project": project or "all",
        "nodes": nodes,
        "edges": list_edges(project=project, state_root=state_root),
        "created_at": store.now_iso(),
    }


def health(project: str | None = None, engine_specs: list[dict] | None = None,
           state_root: Path = store.STATE_ROOT) -> dict:
    objects = list_objects(project=project, state_root=state_root, limit=10000)
    edges = list_edges(project=project, state_root=state_root)
    packets = list_packets(project=project, state_root=state_root)
    evals = list_evals(project=project, state_root=state_root)
    proofs = list_proofs(project=project, state_root=state_root)
    runs = list_engine_runs(project=project, state_root=state_root)
    by_type: dict[str, int] = {}
    by_memory_type: dict[str, int] = {}
    for obj in objects:
        by_type[obj.get("type") or "unknown"] = by_type.get(obj.get("type") or "unknown", 0) + 1
        mt = obj.get("memory_type") or ""
        if mt:
            by_memory_type[mt] = by_memory_type.get(mt, 0) + 1
    linked = {e.get("from_id") for e in edges} | {e.get("to_id") for e in edges}
    evidence = [o for o in objects if o.get("type") in {"evidence_item", "source_event", "work_sample", "feedback_event"}]
    processed_evidence = {e.get("from_id") for e in edges if e.get("type") == "extracted_from"}
    unprocessed = [o for o in evidence if o.get("id") not in processed_evidence]
    orphans = [o for o in objects if o.get("id") not in linked and o.get("type") != "evidence_item"]
    warnings = []
    if unprocessed:
        warnings.append(f"{len(unprocessed)} evidence items still need extraction")
    if orphans:
        warnings.append(f"{len(orphans)} objects have no graph links")
    low_conf = [o for o in objects if float(o.get("confidence") or 0) < 0.35]
    if low_conf:
        warnings.append(f"{len(low_conf)} low-confidence objects need review")
    engine_health = _engine_health(runs, engine_specs or [])
    next_actions = []
    if unprocessed:
        next_actions.append(f"Process {len(unprocessed)} unextracted evidence items")
    if orphans:
        next_actions.append(f"Link or archive {len(orphans)} orphan objects")
    if not proofs and evals:
        next_actions.append("Create proof from latest before/after")
    if not packets and objects:
        next_actions.append("Compile an agent packet from stored objects")
    return CoreHealth(
        project=project or "all",
        object_count=len(objects),
        edge_count=len(edges),
        evidence_count=len(evidence),
        memory_count=sum(1 for o in objects if o.get("type") in MEMORY_OBJECT_TYPES),
        eval_count=len(evals) + by_type.get("eval_check", 0),
        packet_count=len(packets),
        feedback_count=by_type.get("feedback_event", 0),
        proof_count=len(proofs),
        engine_count=len(engine_specs or []),
        warning_count=len(warnings),
        unprocessed_evidence_count=len(unprocessed),
        orphan_object_count=len(orphans),
        low_confidence_count=len(low_conf),
        stale_count=sum(1 for o in objects if o.get("status") == "stale"),
        by_type=by_type,
        by_memory_type=by_memory_type,
        engine_health=engine_health,
        warnings=warnings,
        next_actions=next_actions,
        created_at=store.now_iso(),
    ).model_dump()


def _engine_health(runs: list[dict], engine_specs: list[dict]) -> list[dict]:
    by_engine: dict[str, list[dict]] = {}
    for run in runs:
        by_engine.setdefault(run.get("engine_id") or "", []).append(run)
    out = []
    for spec in engine_specs:
        sid = spec.get("id")
        latest = by_engine.get(sid, [None])[0]
        status = "healthy" if latest and latest.get("status") == "ok" else "idle"
        warning_count = int((latest or {}).get("warning_count") or 0)
        if warning_count:
            status = "warning"
        out.append({
            "id": sid,
            "name": spec.get("name"),
            "status": status,
            "last_run": (latest or {}).get("created_at"),
            "objects_produced": len((latest or {}).get("output_ids") or []),
            "warning_count": warning_count,
        })
    return out
