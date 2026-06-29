# Catalyst control panel

Optional local command center for the Catalyst Brain. It operates on the real markdown under `outputs/<name>/`. It is not required: point any agent at `AGENTS.md` instead.

The canonical local UI at `/` is the React command center:

```txt
Promise -> Connect agent -> Source permission -> Build status -> Command center
```

It connects an agent first because the agent is the v0 builder. The local UI stores scan permission in `.catalyst/permissions.json`, displays `outputs/<name>/BUILD-STATUS.json`, renders the brain graph, and gives MCP/agent instructions. It does not pretend to run live OAuth connectors or build the brain alone.

The legacy vanilla panel remains available at `/legacy/` as a dev fallback.

## Local JSON API

| endpoint | method | purpose |
|----------|--------|---------|
| `/api/status` | GET | brains, permission state, BYOK mode |
| `/api/agents/status` | GET | connection modes + safe CLI detection |
| `/api/connect/prompts` | GET | Claude/Codex/Cursor/Hermes/manual MCP prompts and commands |
| `/api/permissions` | GET/POST | local permission config under `.catalyst/` |
| `/api/build/status?name=` | GET | status-file timeline from `outputs/<name>/BUILD-STATUS.json` |
| `/api/runtime/health` | GET | hybrid runtime health, history, and brain section readiness |
| `/api/core/health` | GET | Core V1 object, engine, memory, graph, packet, feedback, and proof health |
| `/api/core/graph` | GET | Core V1 object graph |
| `/api/core/engines` | GET | 12 engine specs and contracts |
| `/api/brain/sections` | GET | structured section summary and extracted rule counts |
| `/api/proposals` | GET | pending or historical brain update proposals |
| `/api/discover` | GET | read-only source categories, no contents |
| `/api/brain?name=` | GET | brain files grouped by Catalyst section |
| `/api/file` | GET/POST | read / save allowed brain `.md` files, writes under `outputs/` only |
| `/api/context/save` | POST | save pasted context / packet / paths under `outputs/<name>/sources/` |
| `/api/flow/*` | GET/POST | deterministic local routing/context/evaluation/feedback/audit |
| `/api/brain/context` | POST | compact task context packet for agents |
| `/api/evaluate` | POST | structured output evaluation against the local brain |
| `/api/feedback` | POST | classify feedback and create update proposals |
| `/api/proposals/apply` | POST | apply or reject a proposal with history snapshotting |
| `/api/core/ingest` | POST | store raw evidence with provenance and scope |
| `/api/core/extract` | POST | run deterministic Core V1 extraction |
| `/api/core/packet` | POST | compile a Core V1 agent packet |
| `/api/core/evaluate` | POST | evaluate output against packet-linked checks |
| `/api/core/feedback` | POST | capture feedback, update objects, and create proof |
| `/api/export` | GET | brain path + agent prompt |

No shell endpoint. No arbitrary filesystem access.

## Run

```txt
py catalyst.py
py catalyst.py --no-open
python apps/control-panel/server.py
```

Open `http://127.0.0.1:8765`. Stop with Ctrl+C in the terminal.

## Layout

```txt
apps/control-panel/
  server.py        # stdlib HTTP server + allowlisted JSON API
  byok.py          # optional provider abstraction: mock (no key) + OpenRouter
  static/          # legacy vanilla panel at /legacy/
  README.md
apps/web/
  src/             # React command center served at /
  dist/            # built static UI
```

## Config

| var | default | purpose |
|-----|---------|---------|
| `CATALYST_HOST` | `127.0.0.1` | bind host. non-local requires `CATALYST_TOKEN` |
| `CATALYST_PORT` | `8765` | bind port |
| `CATALYST_TOKEN` | _(empty)_ | bearer token required only for non-local binds |
| `OPENROUTER_API_KEY` | _(empty)_ | optional BYOK key (env only, never committed) |
| `CATALYST_PROVIDER` | `mock` | `mock` or `openrouter` |
| `CATALYST_MODEL` | `openrouter/auto` | model for the real provider |

Copy `.env.example` to `.env` to set these. `.env` and `.catalyst/` are gitignored.

## Security boundary

- localhost-only by default; non-local host refuses to start without a token
- no shell/exec endpoint
- no arbitrary filesystem access
- reads: `outputs/`, `templates/`, `docs/`, `prompts/`, and fixed repo status/config endpoints
- writes: `outputs/` and fixed local config files under `.catalyst/`
- never writes `templates/`
- BYOK key never returned to the browser

See [docs/control-panel.md](../../docs/control-panel.md), [docs/byok.md](../../docs/byok.md), and [docs/mcp.md](../../docs/mcp.md).
