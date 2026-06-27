"""Rich MCP tool implementations for the hybrid Catalyst runtime."""
from __future__ import annotations

from . import brain_manager, context_assembler, feedback_processor, health, proposal_engine, structured_evaluator, versioning


def get_brain_context(task: str, project: str = "default", agent: str = "manual") -> dict:
    if not (task or "").strip():
        return {"error": "task is required"}
    return context_assembler.assemble_context(task, project=project or "default", agent=agent or "manual")


def evaluate_output(task: str, output: str, project: str = "default") -> dict:
    if not (task or "").strip():
        return {"error": "task is required"}
    return structured_evaluator.evaluate_output_structured(task, output or "", project=project or "default")


def capture_feedback(task: str, output: str = "", feedback: str = "", project: str = "default", source: str = "user") -> dict:
    return feedback_processor.capture_feedback_structured(task, output, feedback, project=project or "default", source=source or "user")


def propose_brain_updates(project: str = "default", limit: int = 10, status: str = "pending") -> dict:
    return {"project": project, "proposals": proposal_engine.list_brain_updates(project=project, status=status, limit=limit)}


def apply_brain_update(proposal_id: str, project: str = "default", approve: bool = True) -> dict:
    if not proposal_id:
        return {"error": "proposal_id is required"}
    return proposal_engine.apply_brain_update(proposal_id, project=project, approve=approve)


def list_brain(project: str = "default") -> dict:
    return brain_manager.brain_sections_summary(project)


def get_runtime_health(project: str = "default") -> dict:
    report = health.get_health(project or None)
    report["history"] = versioning.list_history(limit=10)
    return report

