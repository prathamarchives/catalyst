# Catalyst control panel

Optional local control surface for the Catalyst Brain. Zero dependencies — Python standard library plus a vanilla HTML/CSS/JS page. It operates on the real markdown under `outputs/<name>/`. It is not required: point any agent at the repo's `AGENTS.md` instead.

It is a staged setup journey (Apple-inspired black/white), not a tab grid:

```txt
Start → Connect AI → Identity → Context → Permission → Build → Explore → Proof → Agents (MCP)
```

It connects an AI/agent **first** — real synthesis/evaluation needs a worker, and mock is never shown as live.

## Local JSON API (allowlisted)

| endpoint | method | purpose |
|----------|--------|---------|
| `/api/status` | GET | brains, key files, BYOK mode |
| `/api/agents/status` | GET | connection modes + safe CLI detection (`shutil.which`) |
| `/api/extraction-prompt` | GET | copyable context-extraction prompt |
| `/api/discover` | GET | read-only source categories (no contents) |
| `/api/brain?name=` | GET | brain files grouped by job |
| `/api/file` | GET/POST | read / save a brain `.md` (writes: `outputs/` only) |
| `/api/context/save` | POST | save pasted context / packet / paths under `outputs/<name>/sources/` |
| `/api/build` | POST | scaffold + honest staged build log |
| `/api/byok/test`, `/api/synthesize` | POST | optional provider call (mock with no key) |
| `/api/export` | GET | brain path + agent prompt |

No shell endpoint. No arbitrary filesystem access.

## Run

```txt
py apps/control-panel/server.py
python apps/control-panel/server.py
```

Open `http://127.0.0.1:8765`.

## Layout

```txt
apps/control-panel/
  server.py        # stdlib HTTP server + allowlisted JSON API (the "bridge")
  byok.py          # optional provider abstraction: mock (no key) + OpenRouter
  static/
    index.html     # single-page control panel
    styles.css     # dark, minimal, command-center theme
    app.js         # vanilla JS, talks to the local API
  README.md
```

## Config (env)

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
- no arbitrary filesystem access — paths resolved and confined to allowlisted roots
- reads: `outputs/`, `templates/`, `docs/`, `prompts/`
- writes: `outputs/` and local-only `.catalyst/` only — never `templates/`
- BYOK key never returned to the browser

See [docs/control-panel.md](../../docs/control-panel.md) and [docs/byok.md](../../docs/byok.md).
