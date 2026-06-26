# Catalyst Overnight State

Updated: 2026-06-25

## Phase completed

- Created the local Persona Brain runtime modules under `catalyst_core/`.
- Added event capture, signal extraction, memory atoms, sub-brain routing,
  compiled wiki markdown, graph, recall, review, health, traces, and proposals.
- Wired runtime tools into `tools/mcp_server.py`.
- Wired runtime endpoints into `apps/control-panel/server.py`.
- Added runtime tests in `tests/test_persona_runtime.py`.
- Updated docs for the v0.5 runtime loop.

## Files changed

- `catalyst_core/store.py`
- `catalyst_core/events.py`
- `catalyst_core/signals.py`
- `catalyst_core/memory.py`
- `catalyst_core/subbrains.py`
- `catalyst_core/compiler.py`
- `catalyst_core/graph.py`
- `catalyst_core/recall.py`
- `catalyst_core/traces.py`
- `catalyst_core/proposals.py`
- `catalyst_core/judgment.py`
- `catalyst_core/health.py`
- `catalyst_core/capture.py`
- `catalyst_core/__init__.py`
- `tools/mcp_server.py`
- `apps/control-panel/server.py`
- `tests/test_mcp.py`
- `tests/test_persona_runtime.py`
- `README.md`
- `AGENTS.md`
- `docs/architecture.md`
- `docs/catalyst-flow.md`
- `docs/control-panel.md`
- `docs/mcp.md`
- `docs/persona-runtime.md`
- `MORNING_REPORT.md`

## Tests run

- `py -m pytest tests/test_persona_runtime.py` - passed, 4 tests.
- `py -m pytest tests/test_mcp.py tests/test_persona_runtime.py` - passed, 7 tests.
- `python evals/run_all.py` - passed, all evals.
- `py -m pytest` - passed, 37 tests.
- `cd apps/web && npm run build` - passed after making the Vite script call the package binary through Node.
- `node packages/cli/bin/catalyst.mjs --help` - passed.
- `node packages/cli/bin/catalyst.mjs local --repo <this repo> --no-open` - passed; server printed URL and stop instructions.
- `python catalyst.py --no-open` - passed; server printed URL and stop instructions.
- API smoke passed for `/api/status`, `/api/connect/prompts`, `/api/health`, and `/api/capture`.

## What works

- `capture_event` appends a raw event and compounds it into signals, memory
  atoms, persona nodes, graph state, compiled markdown, health state, and trace.
- `build_context_packet` returns task recall context from memory atoms.
- `review_output` flags weak output against recalled memory and local rules.
- `get_health` reports counts, sub-brain maturity, graph state, orphan files,
  dead links, warnings, and last compile state.
- MCP lists both compatibility tools and new `catalyst_*` runtime tools.
- HTTP API exposes runtime health, events, signals, memories, graph, recall,
  capture, and review.
- `npm run build` works on Windows even when npm shim generation is unreliable,
  because the script calls `node ./node_modules/vite/bin/vite.js build`.

## What is broken or limited

- The runtime extraction is heuristic. It is useful for a local v0 but not a
  semantic extractor.
- The compiled `.catalyst/persona-brain/` is a runtime view, not a replacement
  for the richer agent-built `outputs/<name>/` brain.
- The local UI can read the new API state, but no deep React runtime graph view
  was added in this pass.
- `npm ci` was slow and twice hung before generating `.bin` wrappers in this
  Windows environment. The package tree became usable, and the build script no
  longer depends on `.bin/vite.cmd`.

## Next loop

- Add a React runtime health/recent-captures panel if that becomes the next
  priority.
- Replace heuristic signal extraction with richer local extraction rules after
  real feedback examples accumulate.
