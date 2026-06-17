# control panel

An optional local control surface for the Catalyst Brain. It is not the product. The product is the markdown protocol in `AGENTS.md`; the panel just makes the brain easy to see and operate. Catalyst works fully without it.

## Why it is built this way

The repo is deliberately dependency-free: markdown plus Python standard library, no npm, no `node_modules`, no build step, no database, no account. A heavy web stack would contradict the positioning (lighter and deeper, optional control surface). So the panel is:

- a single Python stdlib HTTP server (`apps/control-panel/server.py`) — the "bridge"
- a vanilla HTML/CSS/JS single page (`apps/control-panel/static/`)
- zero external dependencies; runs with `py apps/control-panel/server.py`

A richer web app (e.g. `apps/web`) remains a future option once there is demand. The protocol and file layout would not change.

## Run

```txt
py apps/control-panel/server.py
python apps/control-panel/server.py
```

Open `http://127.0.0.1:8765`. It binds `127.0.0.1` only.

## The journey

The panel is one staged setup flow with a progress rail, Apple-inspired black/white/minimal, one main idea per screen:

```txt
Start → Connect AI → Identity → Context → Permission → Build → Explore → Proof → Agents (MCP)
```

0. **Start** — what Catalyst is, local control-panel status, no account/database. One CTA: start setup.
1. **Connect AI** — comes first on purpose. Catalyst needs a worker to synthesize/evaluate/update; without one it only copies empty templates. Modes: Mock/offline (always, no network), OpenRouter BYOK (env key), detected CLIs — Claude Code / Codex / Hermes (existence-only detection, login state unknown), and Manual LLM prompt (always). Each card shows real status; the UI never implies a live model exists when only mock is available.
2. **Identity** — five sharp answers (name, agent jobs, goals/projects, never-ship, first proof task). Not an interview.
3. **Context** — paste a context dump, name manual paths, copy the extraction prompt for any LLM and paste the structured packet back. Connector cards (Notion/Slack/Discord/workspace) are labeled honestly as export/drop/paths — not live OAuth. Saved under `outputs/<name>/sources/`.
4. **Permission** — read-only discovery shown as category counts, the safe-scan explanation with exclusions, and approve / edit / skip. Content scanning stays consent-gated.
5. **Build** — an honest staged build (prepare packet → synthesize identity/context → extract standards/judgment → extract rejected/anti-slop → write skills/workflows/evals → proof setup), labeled live (BYOK) or mock/no-key seed.
6. **Explore** — the brain grouped by job (Who/why · Taste/standards · Operating system · Learning), each file showing what it controls and when agents load it. Edit + save to disk.
7. **Proof** — "Memory tells the agent what exists. Judgment tells it what you would ship." Shows loaded files, mode, a standards review (live or clearly-marked mock preview), and what feedback would update.
8. **Agents (MCP)** — the local MCP scaffold and connector instructions so multiple agents can use the brain. See [mcp.md](mcp.md).

## Security

- binds `127.0.0.1` by default; a non-local host refuses to start without `CATALYST_TOKEN`
- no shell or exec endpoint of any kind
- no arbitrary filesystem access: every path is resolved and must stay inside an allowlisted repo-relative root
- reads limited to `outputs/`, `templates/`, `docs/`, `prompts/`
- writes limited to `outputs/` and the local-only `.catalyst/` config; `templates/` are never written (protocol: never overwrite templates)
- the BYOK key is never returned to the browser

## Without the UI

Everything the panel does, an agent can do from `AGENTS.md`. The Export tab exists to make that explicit: the brain is just local markdown.
