# Morning Report

Date: 2026-06-25

## Built

Catalyst now has a local Persona Brain runtime loop:

```txt
recall -> work -> capture -> extract -> update -> compile -> recall
```

New backend modules store raw events, extract learning signals, turn signals into
memory atoms, route memory into sub-brains, compile a wiki-style Persona Brain,
save a graph, write traces, create proposals, recall task context, review
output, and report health.

The runtime is local-first:

- no cloud service
- no auth system
- no payment system
- no vector database
- no shell endpoint
- runtime writes under `.catalyst/`
- generated user brains still live under gitignored `outputs/`

## Works

- `catalyst_core.capture.capture_event(...)` appends an event and runs the full
  local pipeline.
- `catalyst_core.recall.build_context_packet(...)` returns task context from
  memory atoms and sub-brains.
- `catalyst_core.judgment.review_output(...)` writes review logs and flags weak
  output using recalled memory plus local quality rules.
- `catalyst_core.health.get_health(...)` reports event, signal, memory, graph,
  sub-brain, orphan, dead-link, trace, recall, and review health.
- MCP exposes runtime tools:
  `catalyst_recall`, `catalyst_capture`, `catalyst_search`,
  `catalyst_profile`, `catalyst_review`, `catalyst_health`,
  `catalyst_graph`, and `catalyst_propose_update`.
- The local server exposes runtime endpoints:
  `GET /api/health`, `GET /api/events`, `GET /api/signals`,
  `GET /api/memories`, `GET /api/graph`, `POST /api/recall`,
  `POST /api/capture`, and `POST /api/review`.

## Tests run

- `py -m pytest tests/test_persona_runtime.py` - passed, 4 tests.
- `py -m pytest tests/test_mcp.py tests/test_persona_runtime.py` - passed, 7 tests.
- `python evals/run_all.py` - passed, all evals.
- `py -m pytest` - passed, 37 tests.
- `cd apps/web && npm run build` - passed.
- `node packages/cli/bin/catalyst.mjs --help` - passed.
- `node packages/cli/bin/catalyst.mjs local --repo <this repo> --no-open` - passed; server started and printed URL/stop instructions.
- `python catalyst.py --no-open` - passed; server started and printed URL/stop instructions.
- API smoke passed for `/api/status`, `/api/connect/prompts`, `/api/health`,
  and `/api/capture`. The capture smoke verified event -> signal -> memory ->
  graph -> compile through HTTP.

## Failed and fixed

- Initial runtime tests failed because `catalyst_core/compiler.py` had a missing
  string-concatenation operator. Fixed and reran targeted tests.
- The generated `used_by` link was pointed at a file not produced by the
  compiler. It now points at `agent-interface/agent-contract`.
- `npm ci` twice hung in this Windows environment before completing npm shim
  generation. The dependency tree became usable, and `apps/web/package.json`
  now calls Vite through `node ./node_modules/vite/bin/vite.js` so
  `npm run build` does not depend on `.bin/vite.cmd`.

## Limits

- Extraction is heuristic and conservative. It is enough for local v0 event
  compounding, not a deep semantic parser.
- The compiled `.catalyst/persona-brain/` is a runtime view. The richer
  `outputs/<name>/` Catalyst Brain remains the agent-built deliverable.
- This pass prioritized backend, MCP, API, docs, and tests. The React UI was not
  expanded beyond the existing API/status hooks.

## Next tasks

- Run full verification across evals, pytest, web build, CLI, and local API.
- Add a small React panel for recent captures and runtime health if desired.
- Add richer extraction rules after real user feedback examples accumulate.
