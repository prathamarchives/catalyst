# Persona Brain runtime

Catalyst now has a local runtime loop for agents:

```txt
recall -> work -> capture -> extract -> update -> compile -> recall
```

The runtime is stdlib-only and writes under `.catalyst/`. Generated user-facing
brains still live under `outputs/<name>/`; the runtime state is the local event
store, signal store, memory atom store, graph, traces, health reports, and
proposals used to compile the Persona Brain.

## Data flow

1. `catalyst_capture` appends a raw event.
2. The event becomes one or more signals.
3. Signals become memory atoms, with simple merge-on-same-text behavior.
4. Memory atoms route into sub-brains such as standards, judgment, taste,
   workflow, feedback, context, and agent-interface.
5. The compiler writes markdown under `.catalyst/persona-brain/` with
   frontmatter, parent links, related links, source memory rows, and open
   questions.
6. The graph records event -> signal -> memory -> persona node -> sub-brain
   edges.
7. Recall selects useful sub-brains for a task and returns a context packet.
8. Review checks output against recalled memory plus local quality rules.

## Runtime files

```txt
.catalyst/
  events/events.jsonl
  signals/signals.jsonl
  memories/memories.jsonl
  persona-nodes/nodes.jsonl
  persona-brain/
  graph/graph.json
  traces/traces.jsonl
  proposals/proposals.jsonl
  logs/
    recall.jsonl
    reviews.jsonl
    health.json
    last-compile.json
```

No cloud service, auth system, vector store, embedding model, or payment system
is required for this loop.

## Agent tools

MCP exposes both the older file-brain tools and the runtime tools:

```txt
catalyst_recall
catalyst_capture
catalyst_search
catalyst_profile
catalyst_review
catalyst_health
catalyst_graph
catalyst_propose_update
```

The intended agent behavior is:

```txt
call catalyst_recall before work
produce the work
call catalyst_review before showing important output
call catalyst_capture after user approval, rejection, correction, or task end
call catalyst_health periodically
```

## HTTP API

The local server exposes the same runtime through allowlisted endpoints:

```txt
GET  /api/health
GET  /api/events
GET  /api/signals
GET  /api/memories
GET  /api/graph
POST /api/recall
POST /api/capture
POST /api/review
```

These endpoints do not run shell commands and do not accept arbitrary file
paths. Writes are restricted to the known local runtime state.

## Health

`catalyst_health` reports:

- event, signal, memory, trace, recall, review, and proposal counts
- sub-brain maturity
- graph node and edge counts
- orphan compiled brain files
- dead wiki links
- missing index files
- warnings when the brain has no events, memories, graph, or compiled files

This lets agents and the local UI tell whether the Persona Brain is actually
forming or still waiting for useful signal.
