# Catalyst Core Architecture

Catalyst Core is Layer 2: the cognitive kernel between evidence sources and agents.

```mermaid
flowchart TD
  Evidence["Layer 1 evidence"] --> API["Core Python API"]
  API --> Events["Event log"]
  Events --> Runtime["Mutation runtime"]
  Runtime --> Store["SQLite canonical store"]
  Store --> Graph["Cognitive graph"]
  Store --> Retrieval["Hybrid retrieval"]
  Retrieval --> Packet["Agent packet"]
  Packet --> Eval["Eval runtime"]
  Eval --> Feedback["Feedback learner"]
  Feedback --> Runtime
```

The core implementation is split into:

- `domain/`: typed contracts
- `storage/`: SQLite, graph, FTS, vector fallback, artifacts
- `kernel/`: event log, mutation runtime, retrieval, packet, eval, feedback, proof
- `engines/`: engine contracts and concrete proposers
- `policies/`: scoring, confidence, decay, consolidation, contradiction
- `api/`: Python service boundary

Design laws:

- SQLite is canonical local state.
- Every state change starts as an immutable event.
- Engines propose mutations and never write directly.
- JSONL and markdown are exports only.
- UI, CLI, MCP, and hosted surfaces are clients.

