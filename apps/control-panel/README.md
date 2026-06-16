# Catalyst control panel

Optional local control surface for the Catalyst Brain. Zero dependencies — Python standard library plus a vanilla HTML/CSS/JS page. It operates on the real markdown under `outputs/<name>/`. It is not required: point any agent at the repo's `AGENTS.md` instead.

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
