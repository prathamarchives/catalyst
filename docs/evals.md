# Core Evals

Core V1 evaluates the whole mechanism, not only final text.

## Eval families

| family | question |
|--------|----------|
| Evidence | Does evidence preserve source, type, scope, and provenance? |
| Extraction | Are extracted objects actionable, scoped, and evidence-backed? |
| Memory | Are objects typed, current, linked, and useful? |
| Graph | Can provenance and update paths be traced? |
| Retrieval | Did the task retrieve standards, negative constraints, examples, and current context? |
| Packet | Is the packet concise, scoped, and agent-usable? |
| Output | Does the output pass standards, judgment, taste, task fit, and anti-pattern checks? |
| Feedback | Did feedback create updates and future retrieval changes? |
| System | Are repeated mistakes decreasing and proof records increasing? |

## Implemented checks

The deterministic Core V1 path currently checks:

- rejected evidence creates `taste_delta`, `judgment_atom`, `anti_pattern`, `standard_atom`, and `eval_check`
- every extracted object links back to evidence
- packets include anti-patterns and eval checks
- output review detects generic/slop terms and linked anti-patterns
- feedback creates new evidence, extracted updates, graph edges, and proof records
- health reports engine count, evidence, memory, packet, feedback, proof, orphan, and low-confidence counts

Regression coverage lives in:

```txt
tests/test_core_v1.py
evals/core_v1_check.py
```
