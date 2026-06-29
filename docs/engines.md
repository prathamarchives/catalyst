# Core Engines

Core V1 defines 12 engines in `catalyst_core/core_engines.py`. Each engine has a purpose, inputs, outputs, retrieval role, consolidation role, feedback role, eval hooks, health metrics, and failure modes.

| engine | role |
|--------|------|
| Evidence Engine | normalize raw evidence with provenance and scope |
| Signal Extraction Engine | extract actionable candidate objects |
| Taste Engine | model approval/rejection/edit taste deltas and rules |
| Judgment Engine | model pass/fail/ship/revise decision logic |
| Identity Engine | track evolving self-definition, goals, constraints, boundaries |
| Context Engine | maintain current task, phase, deadline, audience, priorities |
| Memory Engine | store typed memory objects and confidence/staleness |
| Consolidation Engine | merge repeated signals while preserving evidence |
| Contradiction and Scope Engine | detect conflicts and assign scope |
| Retrieval Engine | rank useful objects for a task |
| Agent Packet Engine | compile concise task-specific operating packets |
| Eval and Feedback Engine | judge outputs, capture feedback, create updates and proof |

## Current implementation

The first implementation is deterministic and local:

- `ingest_evidence(...)`
- `run_extraction(...)`
- `retrieve_for_task(...)`
- `compile_agent_packet(...)`
- `evaluate_output(...)`
- `capture_feedback(...)`
- `health(...)`
- `graph(...)`

This is intentionally not a model-dependent extractor yet. The goal is to prove the vertical loop and object/graph contracts before adding heavier extraction or embedding dependencies.

## Health

`GET /api/core/health` reports engine status from `engine-runs.jsonl`, object counts, unprocessed evidence, orphan objects, low-confidence objects, proof count, and next actions.
