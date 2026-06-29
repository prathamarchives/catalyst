"""Engine registry."""
from __future__ import annotations

from catalyst_core.domain.engines import EngineSpec


def spec(engine_id: str, name: str, purpose: str, outputs: list[str]) -> EngineSpec:
    return EngineSpec(
        id=engine_id,
        name=name,
        purpose=purpose,
        inputs=["typed core state"],
        outputs=outputs,
        mutation_rules=["engines propose mutations; mutation runtime validates and commits"],
        eval_hooks=["traceable provenance", "scoped output", "state mutation goes through event log"],
        health_metrics=["engine_run_count", "mutation_count", "warning_count"],
        failure_modes=["unscoped mutation", "missing evidence", "direct state mutation"],
        confidence_behavior="confidence changes only through policy-scored mutations",
    )


ENGINE_SPECS = [
    spec("evidence_engine", "Evidence Normalization Engine", "Normalize raw evidence into evidence items.", ["evidence_items"]),
    spec("signal_extraction_engine", "Signal Extraction Engine", "Extract cognitive signals from evidence.", ["candidate objects"]),
    spec("memory_engine", "Memory Formation Engine", "Assign signals to memory families.", ["memory objects"]),
    spec("taste_engine", "Taste Modeling Engine", "Model taste from approvals, rejections, and edits.", ["taste_delta"]),
    spec("judgment_engine", "Judgment Modeling Engine", "Model ship/revise/reject rules.", ["judgment_atom"]),
    spec("identity_engine", "Identity Modeling Engine", "Track stable identity and boundaries.", ["identity_atom"]),
    spec("context_engine", "Context State Engine", "Track active context and scope.", ["context_atom"]),
    spec("consolidation_engine", "Consolidation Engine", "Merge repeated signals while preserving provenance.", ["consolidated objects"]),
    spec("contradiction_scope_engine", "Contradiction / Scope Engine", "Detect conflicts and create scoped exceptions.", ["contradiction edges"]),
    spec("retrieval_engine", "Retrieval Planning Engine", "Plan hybrid retrieval and produce traces.", ["retrieval_run"]),
    spec("packet_engine", "Packet Compilation Engine", "Compile task-specific agent packets.", ["agent_packet"]),
    spec("eval_feedback_engine", "Eval + Feedback Learning Engine", "Evaluate output and learn from feedback.", ["eval_result", "feedback updates"]),
]

