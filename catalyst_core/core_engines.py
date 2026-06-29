"""Executable Catalyst Core V1 engine scaffolds.

The engines are deterministic first. They create inspectable objects and graph
links that prove the mechanism before any model or embedding dependency exists.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import core_store, recall, store
from .models.core import AgentPacket, CoreEvalResult, CoreObject, EngineRun, EngineSpec

MEMORY_TYPES = [
    "episodic",
    "semantic",
    "procedural",
    "preference",
    "negative",
    "reference",
    "social_customer",
    "strategic",
]

ENGINE_SPECS = [
    EngineSpec(
        id="evidence_engine",
        name="Evidence Engine",
        purpose="Normalize raw evidence into structured evidence records with provenance and scope.",
        inputs=["raw evidence", "feedback", "work samples", "references"],
        outputs=["evidence_item", "source_event", "work_sample", "feedback_event", "reference_item"],
        retrieval_role="Preserves source metadata and task scope for future retrieval.",
        consolidation_role="Groups evidence by project, type, task, audience, and artifact.",
        feedback_role="Stores user correction/review events as first-class evidence.",
        eval_hooks=["source preserved", "type classified", "scope present", "traceable provenance"],
        health_metrics=["evidence_count", "unprocessed_evidence_count", "evidence_with_missing_scope"],
        failure_modes=["raw evidence without provenance", "everything classified as generic note", "missing task/audience scope"],
    ),
    EngineSpec(
        id="signal_extraction_engine",
        name="Signal Extraction Engine",
        purpose="Extract actionable cognitive signals from evidence.",
        inputs=["evidence_item", "feedback_event", "work_sample", "reference_item"],
        outputs=["candidate_memory_atom", "candidate_judgment_atom", "candidate_taste_delta", "candidate_eval_check"],
        retrieval_role="Creates candidate objects retrieval can rank.",
        consolidation_role="Feeds repeated signals into stronger rules.",
        feedback_role="Turns corrections into concrete deltas.",
        eval_hooks=["signal cites evidence", "signal is scoped", "signal is actionable"],
        health_metrics=["signals_extracted_per_evidence", "low_confidence_signal_count", "unscoped_signal_count"],
        failure_modes=["vague claims", "hallucinated preferences", "unactionable standards"],
    ),
    EngineSpec(
        id="taste_engine",
        name="Taste Engine",
        purpose="Model subjective taste from approvals, rejections, edits, and references.",
        inputs=["approved_reference", "rejected_reference", "edits", "taste_delta"],
        outputs=["taste_delta", "taste_rule", "aesthetic_constraint", "tone_constraint"],
        retrieval_role="Supplies task-scoped taste rules and examples.",
        consolidation_role="Clusters repeated taste deltas without flattening nuance.",
        feedback_role="Updates taste rules after approval/rejection/edit.",
        eval_hooks=["matches approved examples", "avoids rejected patterns", "preserves specificity"],
        health_metrics=["taste_delta_count", "taste_rules_with_examples", "taste_rules_used_in_packets"],
        failure_modes=["adjective soup", "unscoped vibe labels", "ignoring context differences"],
    ),
    EngineSpec(
        id="judgment_engine",
        name="Judgment Engine",
        purpose="Model pass/fail decision logic.",
        inputs=["approvals", "rejections", "review comments", "task outcomes"],
        outputs=["judgment_atom", "pass_rule", "fail_rule", "decision_rule", "rejection_pattern"],
        retrieval_role="Supplies what ships, fails, or needs revision.",
        consolidation_role="Strengthens repeated decisions into rules.",
        feedback_role="Captures review decisions and reasons.",
        eval_hooks=["would the user ship it", "known judgment violation", "revision path implied"],
        health_metrics=["judgment_atoms_count", "decisions_with_reasons", "repeated_rejection_patterns"],
        failure_modes=["opinions without criteria", "taste/judgment conflation", "unknown ship bar"],
    ),
    EngineSpec(
        id="identity_engine",
        name="Identity Engine",
        purpose="Track stable but evolving self-definition, goals, constraints, values, and boundaries.",
        inputs=["self-statements", "goals", "positioning", "not-me rejections"],
        outputs=["identity_atom", "goal_atom", "worldview_atom", "constraint_atom", "boundary_atom"],
        retrieval_role="Adds relevant identity and boundary signals to packets.",
        consolidation_role="Retires stale identity and preserves scoped changes.",
        feedback_role="Updates identity when the user says what is or is not them.",
        eval_hooks=["does not box user into stale label", "respects boundaries", "supports current goal"],
        health_metrics=["active_identity_atoms", "stale_identity_atoms", "identity_conflicts"],
        failure_modes=["static persona lock-in", "overused labels", "ignoring updated self-definition"],
    ),
    EngineSpec(
        id="context_engine",
        name="Context Engine",
        purpose="Maintain what matters right now: task, phase, deadline, project state, audience, constraints.",
        inputs=["current task", "project phase", "recent decisions", "constraints"],
        outputs=["context_atom", "active_goal", "current_phase", "task_context", "priority_context"],
        retrieval_role="Boosts active context and current phase.",
        consolidation_role="Expires stale context and links active context to memories.",
        feedback_role="Updates active context after new task or correction.",
        eval_hooks=["packet reflects current priority", "output respects constraints", "old direction avoided"],
        health_metrics=["active_context_items", "stale_context_items", "context_coverage_in_packets"],
        failure_modes=["old goals dominate", "whole-history retrieval", "deadlines ignored"],
    ),
    EngineSpec(
        id="memory_engine",
        name="Memory Engine",
        purpose="Store and manage the eight memory types as connected objects.",
        inputs=["signals", "feedback", "eval results", "packets"],
        outputs=["typed memory objects", "memory links", "staleness markers"],
        retrieval_role="Provides typed objects to retrieval.",
        consolidation_role="Validates memory type, evidence, scope, and confidence.",
        feedback_role="Updates confidence and maturity after use.",
        eval_hooks=["typed correctly", "scoped", "evidence present", "useful for future task"],
        health_metrics=["memory_count_by_type", "orphan_memory_count", "stale_memory_count"],
        failure_modes=["generic note bucket", "no provenance", "stale memory dominates"],
    ),
    EngineSpec(
        id="consolidation_engine",
        name="Consolidation Engine",
        purpose="Merge repeated signals into stronger rules while preserving evidence.",
        inputs=["candidate objects", "repeated signals", "feedback events"],
        outputs=["consolidated_standard", "consolidated_taste_rule", "cluster_summary", "conflict_notice"],
        retrieval_role="Makes repeated rules easier to retrieve.",
        consolidation_role="Clusters and merges with scope and source preservation.",
        feedback_role="Promotes repeated corrections into stronger rules.",
        eval_hooks=["source evidence preserved", "scope added", "exceptions retained"],
        health_metrics=["clusters_created", "duplicate_signal_reduction", "conflicts_detected"],
        failure_modes=["over-compression", "contradictions merged", "source loss"],
    ),
    EngineSpec(
        id="contradiction_scope_engine",
        name="Contradiction and Scope Engine",
        purpose="Detect contradictions and assign scope instead of treating memory as globally true.",
        inputs=["memory objects", "taste rules", "identity atoms", "standards", "task contexts"],
        outputs=["contradiction_record", "scoped_exception", "scope_boundary"],
        retrieval_role="Prevents wrong-scope memories from entering packets.",
        consolidation_role="Separates global rules from scoped exceptions.",
        feedback_role="Creates scope exceptions when corrections conflict.",
        eval_hooks=["global or task-specific", "known exception", "right scoped version used"],
        health_metrics=["open_contradictions", "scoped_exceptions", "resolved_conflicts"],
        failure_modes=["preference contamination", "old memory override", "hidden contradictions"],
    ),
    EngineSpec(
        id="retrieval_engine",
        name="Retrieval Engine",
        purpose="Select the most useful objects for a task.",
        inputs=["task", "active context", "memory objects", "standards", "evals", "references"],
        outputs=["retrieval_set", "ranked_objects", "retrieval_trace", "missing_context_notice"],
        retrieval_role="The ranking core for task packets.",
        consolidation_role="Records object usefulness for future ranking.",
        feedback_role="Updates retrieval usefulness after packet success/failure.",
        eval_hooks=["relevant standards included", "negative constraints included", "stale memory avoided"],
        health_metrics=["retrieval_precision_proxy", "packet_success_rate", "missed_memory_failures"],
        failure_modes=["semantic-nearest but task-useless", "context dump", "missing negative constraints"],
    ),
    EngineSpec(
        id="agent_packet_engine",
        name="Agent Packet Engine",
        purpose="Compile retrieved objects into concise task-specific instructions for agents.",
        inputs=["task", "retrieval_set", "active context", "standards", "examples", "anti-patterns"],
        outputs=["agent_packet", "packet_trace", "agent_instruction", "eval_checklist"],
        retrieval_role="Presents retrieved objects as usable instructions.",
        consolidation_role="Logs packet performance for future compaction.",
        feedback_role="Connects feedback to the packet that caused the output.",
        eval_hooks=["short enough", "constraints/examples/evals included", "improves output"],
        health_metrics=["packets_created", "average_packet_size", "packet_success_rate"],
        failure_modes=["too long", "missing key standard", "vague taste words", "no eval checks"],
    ),
    EngineSpec(
        id="eval_feedback_engine",
        name="Eval and Feedback Engine",
        purpose="Judge outputs, collect feedback, convert feedback into updates, and create proof.",
        inputs=["agent output", "agent packet", "eval checks", "approval/rejection/edit"],
        outputs=["eval_result", "feedback_event", "updated_objects", "proof_record"],
        retrieval_role="Creates eval and feedback objects that future retrieval can use.",
        consolidation_role="Promotes repeated failures into stronger eval checks.",
        feedback_role="The system learning loop after correction.",
        eval_hooks=["output quality", "feedback creates update", "future behavior improves"],
        health_metrics=["feedback_events", "proof_records", "repeated_failure_count"],
        failure_modes=["feedback not stored", "evals not updated", "no before/after proof"],
    ),
]

ENGINE_BY_ID = {spec.id: spec for spec in ENGINE_SPECS}
NEGATIVE_TERMS = ["generic", "cringe", "off-brand", "fake", "low-quality", "wrong", "reject", "never", "do not", "don't", "slop"]
APPROVAL_TERMS = ["approved", "ship", "works", "good", "keep", "strong"]
SLOP_TERMS = ["unlock", "seamless", "supercharge", "productivity platform", "revolutionary", "game changer"]


def engine_specs() -> list[dict]:
    return [spec.model_dump() for spec in ENGINE_SPECS]


def ingest_evidence(raw_content: str, evidence_type: str = "evidence_item", source: str = "manual",
                    project: str = "default", task_type: str = "", audience: str = "",
                    artifact_type: str = "", outcome: str = "", actor: str = "user",
                    sensitivity: str = "normal", tags: list[str] | None = None,
                    state_root: Path = store.STATE_ROOT) -> dict:
    if not (raw_content or "").strip():
        return {"error": "raw_content is required"}
    etype = evidence_type if evidence_type in {"evidence_item", "source_event", "work_sample", "feedback_event", "reference_item"} else "evidence_item"
    summary = _summarize(raw_content)
    obj = CoreObject(
        id=store.new_id("evidence"),
        type=etype,
        title=summary[:90],
        content=raw_content.strip(),
        summary=summary,
        project=project or "default",
        task_type=task_type or recall.classify_task(raw_content),
        audience=audience,
        scope=artifact_type or task_type or "general",
        confidence=0.9,
        source_strength=0.9 if etype in {"feedback_event", "work_sample", "reference_item"} else 0.65,
        status="active",
        memory_type="episodic",
        engine_id="evidence_engine",
        evidence_ids=[],
        tags=(tags or []) + [etype],
        metadata={
            "source": source,
            "actor": actor,
            "artifact_type": artifact_type,
            "outcome": outcome,
            "sensitivity": sensitivity,
            "raw_content": raw_content.strip(),
        },
    )
    saved = core_store.save_object(obj, state_root)
    _save_run("evidence_engine", project, [], [saved["id"]], [], state_root)
    return saved


def run_extraction(evidence_id: str | None = None, project: str = "default",
                   state_root: Path = store.STATE_ROOT) -> dict:
    evidence_items = core_store.list_objects(project=project, state_root=state_root, limit=10000)
    evidence_items = [o for o in evidence_items if o.get("type") in {"evidence_item", "source_event", "work_sample", "feedback_event", "reference_item"}]
    if evidence_id:
        evidence_items = [o for o in evidence_items if o.get("id") == evidence_id]
    created: list[dict] = []
    warnings: list[str] = []
    for ev in evidence_items:
        text = " ".join(str(ev.get(k, "")) for k in ("content", "summary"))
        low = text.lower()
        outcome = str((ev.get("metadata") or {}).get("outcome") or "").lower()
        if not ev.get("task_type"):
            warnings.append(f"{ev.get('id')} has no task_type")
        if _is_negative(low, outcome):
            created.extend(_negative_objects(ev, state_root))
        if _is_approval(low, outcome):
            created.extend(_approval_objects(ev, state_root))
        created.extend(_contextual_objects(ev, state_root))
    for engine_id in [
        "signal_extraction_engine", "taste_engine", "judgment_engine", "identity_engine",
        "context_engine", "memory_engine", "consolidation_engine", "contradiction_scope_engine",
    ]:
        _save_run(engine_id, project, [e.get("id") for e in evidence_items], [o["id"] for o in created], warnings, state_root)
    return {"ok": True, "evidence_processed": len(evidence_items), "objects_created": created, "warnings": warnings}


def retrieve_for_task(task: str, project: str = "default", limit: int = 12,
                      state_root: Path = store.STATE_ROOT) -> dict:
    task_type = recall.classify_task(task)
    objects = [o for o in core_store.list_objects(project=project, state_root=state_root, limit=10000)
               if o.get("type") not in {"evidence_item", "source_event", "work_sample", "feedback_event"}]
    scored = []
    for obj in objects:
        score = _score(task, task_type, obj)
        if score > 0:
            scored.append((score, obj))
    ranked = sorted(scored, key=lambda pair: (pair[0], pair[1].get("updated_at", "")), reverse=True)[: max(1, min(50, limit))]
    retrieval_id = store.new_id("retrieval")
    retrieval = CoreObject(
        id=retrieval_id,
        type="retrieval_set",
        title=f"Retrieval for {task[:70]}",
        content=task,
        summary=f"{len(ranked)} objects retrieved for {task_type} task",
        project=project,
        task_type=task_type,
        scope=task_type,
        confidence=round(sum(s for s, _ in ranked) / max(1, len(ranked)), 3),
        source_strength=0.7,
        status="active",
        engine_id="retrieval_engine",
        related_ids=[obj["id"] for _, obj in ranked],
        tags=["retrieval"],
        metadata={"trace": [{"object_id": obj["id"], "score": round(score, 3), "type": obj.get("type")} for score, obj in ranked]},
    )
    saved = core_store.save_object(retrieval, state_root)
    for score, obj in ranked:
        core_store.add_edge(obj["id"], saved["id"], "retrieved_for", project, "retrieval_engine", min(1.0, score), {"task": task}, state_root)
    _save_run("retrieval_engine", project, [], [saved["id"]], [] if ranked else ["no matching objects"], state_root)
    return {"retrieval_set": saved, "objects": [dict(obj, retrieval_score=round(score, 3)) for score, obj in ranked], "task_type": task_type}


def compile_agent_packet(task: str, project: str = "default", limit: int = 12,
                         state_root: Path = store.STATE_ROOT) -> dict:
    retrieval = retrieve_for_task(task, project, limit, state_root)
    objects = retrieval["objects"]
    by_type = _group_by_type(objects)
    eval_checks = by_type.get("eval_check", [])[:5]
    packet_text = _packet_text(task, retrieval["task_type"], by_type, objects)
    confidence = min(1.0, 0.2 + 0.08 * len(objects) + 0.12 * len(eval_checks))
    packet = AgentPacket(
        id=store.new_id("packet"),
        task=task,
        project=project,
        task_type=retrieval["task_type"],
        retrieval_set_id=retrieval["retrieval_set"]["id"],
        object_ids=[o["id"] for o in objects],
        packet=packet_text,
        eval_check_ids=[o["id"] for o in eval_checks],
        trace=[{"object_id": o["id"], "type": o.get("type"), "score": o.get("retrieval_score")} for o in objects],
        confidence=round(confidence, 2),
        created_at=store.now_iso(),
    )
    saved = core_store.save_packet(packet, state_root)
    core_store.add_edge(retrieval["retrieval_set"]["id"], saved["id"], "compiled_into", project, "agent_packet_engine", confidence, {"task": task}, state_root)
    for obj in objects:
        core_store.add_edge(obj["id"], saved["id"], "used_in", project, "agent_packet_engine", float(obj.get("retrieval_score") or 0.5), {}, state_root)
    _save_run("agent_packet_engine", project, [retrieval["retrieval_set"]["id"]], [saved["id"]], [] if objects else ["packet has no retrieved objects"], state_root)
    return {"packet": saved, "objects": objects}


def evaluate_output(packet_id: str, output: str, project: str = "default",
                    state_root: Path = store.STATE_ROOT) -> dict:
    packets = core_store.list_packets(project=project, state_root=state_root)
    packet = next((p for p in packets if p.get("id") == packet_id), None)
    if not packet:
        return {"error": f"packet not found: {packet_id}"}
    objects = [core_store.get_object(oid, state_root) for oid in packet.get("object_ids", [])]
    objects = [o for o in objects if o]
    low = (output or "").lower()
    issues = []
    violated = []
    passed = []
    failed = []
    for obj in objects:
        if obj.get("type") == "anti_pattern" and _object_hits(low, obj):
            violated.append(obj["id"])
            issues.append(f"violates anti-pattern: {obj.get('summary') or obj.get('content')}")
        if obj.get("type") == "eval_check":
            if _object_hits(low, obj):
                failed.append(obj["id"])
            else:
                passed.append(obj["id"])
    for term in SLOP_TERMS:
        if term in low:
            issues.append(f"generic/slop term present: {term}")
    score = max(0.0, min(1.0, 0.75 - 0.18 * len(violated) - 0.08 * len(issues) + 0.04 * len(passed)))
    verdict = "ship" if score >= 0.78 and not issues else "revise" if score >= 0.45 else "reject"
    if not output.strip():
        verdict = "ask"
        issues.append("no output provided")
    result = CoreEvalResult(
        id=store.new_id("eval"),
        packet_id=packet_id,
        project=project,
        task=packet.get("task", ""),
        output=output or "",
        verdict=verdict,
        score=round(score, 2),
        passed_check_ids=passed,
        failed_check_ids=failed,
        violated_object_ids=violated,
        issues=issues,
        created_at=store.now_iso(),
    )
    saved = core_store.save_eval(result, state_root)
    core_store.add_edge(packet_id, saved["id"], "evaluated_by", project, "eval_feedback_engine", score, {"verdict": verdict}, state_root)
    for oid in violated + failed:
        core_store.add_edge(saved["id"], oid, "failed_by", project, "eval_feedback_engine", 0.8, {}, state_root)
    _save_run("eval_feedback_engine", project, [packet_id], [saved["id"]], issues, state_root)
    return saved


def capture_feedback(packet_id: str, output: str, feedback: str, project: str = "default",
                     state_root: Path = store.STATE_ROOT) -> dict:
    if not feedback.strip():
        return {"error": "feedback is required"}
    feedback_obj = ingest_evidence(
        feedback,
        evidence_type="feedback_event",
        source="user_feedback",
        project=project,
        outcome="rejected" if _is_negative(feedback.lower(), "") else "approved" if _is_approval(feedback.lower(), "") else "reviewed",
        state_root=state_root,
    )
    extracted = run_extraction(feedback_obj["id"], project, state_root)
    eval_result = evaluate_output(packet_id, output, project, state_root) if packet_id else {}
    object_ids = [o["id"] for o in extracted.get("objects_created", [])]
    for oid in object_ids:
        core_store.add_edge(feedback_obj["id"], oid, "updated_by", project, "eval_feedback_engine", 0.85, {"feedback": feedback}, state_root)
    proof = None
    if packet_id and output.strip():
        proof = core_store.save_proof({
            "project": project,
            "packet_id": packet_id,
            "before": output,
            "after": "",
            "feedback": feedback,
            "object_ids": object_ids,
            "metadata": {"eval_result_id": eval_result.get("id")},
        }, state_root)
        core_store.add_edge(packet_id, proof["id"], "improved_by", project, "eval_feedback_engine", 0.7, {}, state_root)
        for oid in object_ids:
            core_store.add_edge(oid, proof["id"], "supports", project, "eval_feedback_engine", 0.7, {}, state_root)
    return {"ok": True, "feedback_event": feedback_obj, "extracted": extracted, "eval_result": eval_result, "proof": proof}


def health(project: str | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    return core_store.health(project, engine_specs(), state_root)


def graph(project: str | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    return core_store.graph(project, state_root)


def _negative_objects(ev: dict, state_root: Path) -> list[dict]:
    text = ev.get("content") or ev.get("summary") or ""
    project = ev.get("project") or "default"
    scope = ev.get("task_type") or ev.get("scope") or "general"
    title = _summarize(text, 90)
    specs = [
        ("taste_delta", "preference", "Taste delta from rejection", f"Reject outputs with this feel or pattern: {title}", "taste_engine"),
        ("judgment_atom", "preference", "Judgment atom from rejection", f"Fail work that repeats this rejection reason: {title}", "judgment_engine"),
        ("anti_pattern", "negative", "Anti-pattern", title, "judgment_engine"),
        ("standard_atom", "semantic", "Standard from rejection", f"Good work must avoid: {title}", "signal_extraction_engine"),
        ("eval_check", "procedural", "Eval check from rejection", f"Check output does not repeat this failure: {title}", "eval_feedback_engine"),
    ]
    return [_create_from_evidence(ev, t, mt, ti, body, scope, engine, state_root) for t, mt, ti, body, engine in specs]


def _approval_objects(ev: dict, state_root: Path) -> list[dict]:
    text = ev.get("content") or ev.get("summary") or ""
    project = ev.get("project") or "default"
    scope = ev.get("task_type") or ev.get("scope") or "general"
    title = _summarize(text, 90)
    specs = [
        ("reference_item", "reference", "Approved reference", title, "taste_engine"),
        ("taste_rule", "preference", "Taste rule from approval", f"Prefer work with this approved quality: {title}", "taste_engine"),
        ("standard_atom", "semantic", "Standard from approval", f"Good work should satisfy: {title}", "signal_extraction_engine"),
        ("eval_check", "procedural", "Eval check from approval", f"Check output includes the approved quality: {title}", "eval_feedback_engine"),
    ]
    return [_create_from_evidence(ev, t, mt, ti, body, scope, engine, state_root) for t, mt, ti, body, engine in specs]


def _contextual_objects(ev: dict, state_root: Path) -> list[dict]:
    text = (ev.get("content") or ev.get("summary") or "").strip()
    if not text:
        return []
    created = []
    low = text.lower()
    if any(w in low for w in ("goal", "phase", "deadline", "right now", "current")):
        created.append(_create_from_evidence(ev, "context_atom", "semantic", "Context atom", _summarize(text), ev.get("task_type") or "general", "context_engine", state_root))
    if any(w in low for w in ("i am", "we are", "not me", "identity", "principle", "boundary")):
        created.append(_create_from_evidence(ev, "identity_atom", "semantic", "Identity atom", _summarize(text), ev.get("task_type") or "general", "identity_engine", state_root))
    if not created and ev.get("type") == "evidence_item":
        created.append(_create_from_evidence(ev, "memory_atom", "semantic", "Semantic memory", _summarize(text), ev.get("task_type") or "general", "memory_engine", state_root, confidence=0.45))
    return created


def _create_from_evidence(ev: dict, type: str, memory_type: str, title: str, content: str,
                          scope: str, engine_id: str, state_root: Path,
                          confidence: float = 0.72) -> dict:
    obj = CoreObject(
        id=store.new_id("obj"),
        type=type,
        title=title,
        content=content,
        summary=_summarize(content, 120),
        project=ev.get("project") or "default",
        task_type=ev.get("task_type") or scope,
        audience=ev.get("audience") or "",
        scope=scope,
        confidence=confidence,
        source_strength=float(ev.get("source_strength") or 0.65),
        status="active",
        memory_type=memory_type,
        engine_id=engine_id,
        evidence_ids=[ev["id"]],
        tags=[type, memory_type],
        metadata={"source_evidence_summary": ev.get("summary")},
    )
    saved = core_store.save_object(obj, state_root)
    core_store.add_edge(ev["id"], saved["id"], "extracted_from", ev.get("project") or "default", engine_id, confidence, {}, state_root)
    return saved


def _packet_text(task: str, task_type: str, by_type: dict[str, list[dict]], objects: list[dict]) -> str:
    def lines(label: str, rows: list[dict]) -> list[str]:
        if not rows:
            return [f"{label}:\n- (none retrieved)"]
        return [label + ":"] + [f"- {r.get('summary') or r.get('content')}" for r in rows[:5]]

    parts = [
        f"TASK:\n{task}",
        f"TASK TYPE:\n{task_type}",
        *lines("ACTIVE CONTEXT", by_type.get("context_atom", []) + by_type.get("memory_atom", [])),
        *lines("RELEVANT IDENTITY", by_type.get("identity_atom", [])),
        *lines("STANDARDS", by_type.get("standard_atom", [])),
        *lines("TASTE RULES", by_type.get("taste_rule", []) + by_type.get("taste_delta", [])),
        *lines("JUDGMENT RULES", by_type.get("judgment_atom", [])),
        *lines("ANTI-PATTERNS", by_type.get("anti_pattern", [])),
        *lines("APPROVED REFERENCES", by_type.get("reference_item", [])),
        *lines("EVAL CHECKS", by_type.get("eval_check", [])),
        "WORKFLOW:\n- Use these objects as operating constraints.\n- Produce the work.\n- Review against eval checks and anti-patterns.\n- Capture approval, rejection, or edits after the user reacts.",
    ]
    return "\n\n".join(parts)


def _score(task: str, task_type: str, obj: dict) -> float:
    q = _tokens(task + " " + task_type)
    hay = _tokens(" ".join(str(obj.get(k, "")) for k in ("title", "summary", "content", "scope", "task_type", "tags")))
    if not hay:
        return 0.0
    overlap = len(q & hay) / max(1, len(q))
    type_boost = {
        "anti_pattern": 0.35,
        "judgment_atom": 0.32,
        "standard_atom": 0.3,
        "eval_check": 0.28,
        "taste_rule": 0.25,
        "taste_delta": 0.23,
        "context_atom": 0.22,
        "identity_atom": 0.18,
        "reference_item": 0.16,
    }.get(obj.get("type"), 0.08)
    task_boost = 0.18 if obj.get("task_type") == task_type else 0.0
    confidence = float(obj.get("confidence") or 0.5) * 0.12
    stale_penalty = 0.2 if obj.get("status") == "stale" else 0.0
    return round(max(0.0, overlap + type_boost + task_boost + confidence - stale_penalty), 3)


def _object_hits(output_low: str, obj: dict) -> bool:
    terms = _tokens(obj.get("summary") or obj.get("content") or "")
    if not terms:
        return False
    return len(terms & _tokens(output_low)) >= min(3, max(1, len(terms) // 3))


def _group_by_type(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        out.setdefault(row.get("type") or "unknown", []).append(row)
    return out


def _is_negative(low: str, outcome: str) -> bool:
    return outcome in {"rejected", "failed", "revise"} or any(term in low for term in NEGATIVE_TERMS)


def _is_approval(low: str, outcome: str) -> bool:
    return outcome in {"approved", "shipped", "ship"} or any(term in low for term in APPROVAL_TERMS)


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9][a-z0-9_-]{2,}", (text or "").lower())}


def _summarize(text: str, limit: int = 160) -> str:
    clean = re.sub(r"\s+", " ", (text or "").strip())
    return clean[:limit].rstrip()


def _save_run(engine_id: str, project: str, input_ids: list[str], output_ids: list[str],
              warnings: list[str], state_root: Path) -> dict:
    run = EngineRun(
        id=store.new_id("engrun"),
        engine_id=engine_id,
        project=project or "default",
        status="warning" if warnings else "ok",
        input_ids=input_ids,
        output_ids=output_ids,
        warning_count=len(warnings),
        warnings=warnings,
        created_at=store.now_iso(),
    )
    return core_store.save_engine_run(run, state_root)
