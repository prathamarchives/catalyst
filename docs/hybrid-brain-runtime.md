# Hybrid Brain Runtime

Catalyst uses a hybrid brain model: human-readable markdown stays canonical for the user, while structured runtime objects let agents retrieve, evaluate, learn, and propose updates without dumping the whole brain into context.

## Runtime pieces

| module | role |
|--------|------|
| `catalyst_core/models/brain.py` | typed brain profile, sections, standards, judgment rules, examples, feedback memory, task patterns, decision rules, context sources |
| `catalyst_core/models/events.py` | events, signals, memory atoms, update proposals |
| `catalyst_core/models/evals.py` | structured eval issues, eval results, runtime health |
| `catalyst_core/brain_parser.py` | conservative markdown parser that preserves raw markdown and extracts rule-shaped data |
| `catalyst_core/brain_manager.py` | brain loading, section summaries, validation, missing/placeholder checks |
| `catalyst_core/context_assembler.py` | task routing plus compact context packets for agents |
| `catalyst_core/structured_evaluator.py` | deterministic scores, verdicts, issues, confidence, and proposal suggestions |
| `catalyst_core/feedback_processor.py` | feedback classification, signal capture, memory atom creation, proposal creation |
| `catalyst_core/proposal_engine.py` | proposal listing and apply/reject flow |
| `catalyst_core/versioning.py` | local snapshots and append-only history for accepted updates |
| `catalyst_core/retrieval.py` | lightweight local relevance scoring over sections and memory atoms |
| `catalyst_core/mcp_tools.py` | callable functions backing MCP tools and HTTP endpoints |

## Brain files stay readable

The generated brain stays under:

```txt
outputs/<name>/catalyst-brain/
```

Markdown files remain editable by a person. The parser extracts structured data when it can and stores unknown/freeform markdown on the section object so local notes are not lost. Template or placeholder sections lower confidence instead of pretending alignment is known.

## Feedback becomes proposals

Feedback is classified into:

```txt
style_voice_correction
taste_judgment_correction
rejected_pattern
approved_pattern
factual_context_update
workflow_task_pattern_update
decision_rule
anti_slop_quality_rule
unclear_feedback
```

The processor stores the raw event, extracts signals/memory atoms, then creates proposal records under `.catalyst/proposals/`. Applying a proposal appends an explicit block to the target brain markdown and writes a snapshot/history record under `.catalyst/history/`.

## Evaluation is honest

The evaluator returns:

```txt
verdict: ship | revise | reject | ask
scores:
  standards_alignment
  judgment_alignment
  rejected_pattern_risk
  taste_voice_fit
  task_fit
  specificity_proof_concreteness
  safety_privacy
issues
matched_rules
violated_patterns
suggested_feedback
proposal_ids
confidence
```

When the brain is missing, empty, or still template-like, confidence stays low and the verdict is `ask`. Catalyst should not imply high alignment from placeholder files.

## Context packets are compact

Agents should call `catalyst_get_brain_context` or `POST /api/brain/context` before work. The packet includes relevant sections, selected standards, judgment rules, rejected patterns, approved examples, memory atoms, warnings, and confidence. It does not load every file by default.

## Public local API

The local HTTP server exposes:

```txt
POST /api/brain/context
POST /api/evaluate
POST /api/feedback
GET  /api/proposals
POST /api/proposals/apply
GET  /api/runtime/health
GET  /api/brain/sections
```

These are local-only wrappers around `catalyst_core`. They do not run shell commands and they do not accept arbitrary paths.

## MCP tools

The primary agent tools are:

```txt
catalyst_get_brain_context
catalyst_evaluate_output
catalyst_capture_feedback
catalyst_propose_brain_updates
catalyst_apply_brain_update
catalyst_list_brain
catalyst_get_runtime_health
```

Older file tools remain available for compatibility, but new agents should prefer the hybrid tools above.

## Security boundary

- reads stay within known local roots and fixed status/config endpoints
- writes stay within `outputs/` and `.catalyst/`
- no shell/exec endpoint exists
- no account or hosted backend is required
- browser storage must not hold API keys
- proposals are reviewed or explicitly applied; the runtime never rewrites the brain silently
