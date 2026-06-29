# Core Memory Types

Catalyst Core V1 uses eight memory types. They are fields on typed Core objects, not loose markdown headings.

| memory type | meaning | example object types |
|-------------|---------|----------------------|
| episodic | events that happened | evidence item, feedback event, work sample |
| semantic | stable facts and concepts | memory atom, context atom, standard atom |
| procedural | how work should be done | eval check, workflow rule |
| preference | what the user/team prefers | taste delta, taste rule, judgment atom |
| negative | what to avoid | anti-pattern, rejection pattern |
| reference | approved/rejected examples | reference item |
| social_customer | people, audiences, market reactions | audience/customer atoms |
| strategic | bets, plans, priorities, sequencing | goal/context/strategy atoms |

## Object fields

Core objects include:

```txt
id
type
title
content
summary
project
task_type
audience
scope
confidence
source_strength
status
memory_type
engine_id
evidence_ids
related_ids
contradicts_ids
tags
metadata
```

Statuses are:

```txt
candidate | active | consolidated | stale | contradicted | archived | low_confidence
```

Every object should be traceable to evidence or to another object through graph edges. Orphaned objects are a health warning.
