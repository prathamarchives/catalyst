# Catalyst Core Mechanism

Catalyst Core V1 is a local-first cognitive operating layer for agents.

The mechanism is:

```txt
raw evidence
-> engines
-> typed memory objects
-> interconnected graph
-> retrieval set
-> agent packet
-> output eval
-> feedback update
-> stronger future packet
```

The point is not to store more notes. The point is compounding judgment: every rejection, approval, edit, and shipped artifact should become better taste, judgment, standards, anti-patterns, evals, retrieval, and proof.

## Local state

Core V1 writes local JSONL state under `.catalyst/core/`:

```txt
objects.jsonl
edges.jsonl
engine-runs.jsonl
packets.jsonl
evals.jsonl
proofs.jsonl
```

The generated user brain can still exist under `outputs/<name>/`, and markdown can still be exported for humans. Core V1 is object-first so provenance, graph links, packets, evals, and feedback are inspectable by code.

## Core object path

1. `POST /api/core/ingest` stores raw evidence with project, task, audience, source, outcome, and sensitivity.
2. `POST /api/core/extract` runs deterministic engine scaffolds and creates typed objects.
3. `POST /api/core/packet` retrieves relevant objects and compiles a task-specific packet.
4. `POST /api/core/evaluate` judges an output against packet-linked checks and anti-patterns.
5. `POST /api/core/feedback` stores feedback, extracts new objects, updates the graph, and creates proof when before/after evidence exists.
6. `GET /api/core/health` and `GET /api/core/graph` show whether the system is connected and improving.

## First dogfood workflow

The first proof path is Catalyst on itself:

1. Add a rejected Catalyst landing page draft.
2. Add why it was rejected.
3. Extract taste delta, judgment atom, anti-pattern, standard atom, and eval check.
4. Compile a landing-page agent packet.
5. Evaluate the next output.
6. Feed back the result.
7. Inspect graph links from evidence to objects to packet to eval to proof.

This is the minimum vertical path. If feedback does not change future packets, the system is not Catalyst.
