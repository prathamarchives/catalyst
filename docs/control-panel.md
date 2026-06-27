# control panel

The Catalyst local UI is an optional command center for the Catalyst Brain your agent builds. It is not the product and it is not a hosted app. The product is the local protocol in `AGENTS.md` plus the files under `outputs/<name>/`.

## Run

```txt
py catalyst.py
py catalyst.py --no-open
python apps/control-panel/server.py
```

Open `http://127.0.0.1:8765`. It binds `127.0.0.1` by default. Stop server: press Ctrl+C in the terminal that started Catalyst.

## Current local UI flow

```txt
Promise -> Connect agent -> Source permission -> Build status -> Command center
```

1. **Promise** - "Give your agents your taste, context, and judgment."
2. **Connect agent** - cards/tabs for Claude Code, Codex, Cursor, Hermes, and Manual MCP. Each shows detection when possible, one real command when useful, one copy-paste prompt always, and a manual MCP JSON fallback. These are instructions, not fake OAuth connectors.
3. **Source permission** - recommended safe scan, manual paths only, or skip scan / use typed context. This writes `.catalyst/permissions.json`.
4. **Build status** - waits for `outputs/<name>/BUILD-STATUS.json`. The local UI only displays it; the connected agent writes it while building.
5. **Command center** - active brain name, build timeline, local brain graph, readiness, missing context/open questions, agent instructions, and hosted/founding CTA.

The advanced "Run the loop" tool is collapsed. It is for manual testing of the same local calls your agent uses over MCP; it is not required onboarding.

## API

| endpoint | method | purpose |
|----------|--------|---------|
| `/api/status` | GET | repo root, brains, permission state, BYOK status |
| `/api/agents/status` | GET | connection mode status + safe CLI detection |
| `/api/connect/prompts` | GET | Claude/Codex/Cursor/Hermes/manual MCP commands and prompts |
| `/api/permissions` | GET/POST | read/write `.catalyst/permissions.json` |
| `/api/build/status?name=` | GET | read `outputs/<name>/BUILD-STATUS.json`, or return safe waiting defaults |
| `/api/health` | GET | local runtime health: events, signals, memories, graph, links, warnings |
| `/api/runtime/health` | GET | hybrid runtime health, update history, and brain section readiness |
| `/api/brain/sections` | GET | structured section summary, missing sections, placeholder sections, and extracted rule counts |
| `/api/proposals` | GET | pending or historical brain update proposals |
| `/api/events` | GET | recent captured runtime events |
| `/api/signals` | GET | extracted learning signals |
| `/api/memories` | GET | memory atoms, with optional `query` filter |
| `/api/graph` | GET | runtime graph and summary |
| `/api/recall` | POST | build a task context packet from local runtime memory |
| `/api/capture` | POST | append an event and run extract/update/compile |
| `/api/review` | POST | review output against recalled memory and local quality rules |
| `/api/brain/context` | POST | compact agent context packet for a task |
| `/api/evaluate` | POST | structured evaluation with judgment, taste, rejected-pattern, specificity, and safety scores |
| `/api/feedback` | POST | classify feedback, capture runtime signal, and create update proposals |
| `/api/proposals/apply` | POST | apply or reject one proposal with local history snapshotting |
| `/api/discover` | GET | read-only source categories, no contents |
| `/api/brain?name=` | GET | brain files grouped by Catalyst section |
| `/api/file` | GET/POST | read/save allowed markdown under `outputs/` only |
| `/api/flow/*` | GET/POST | deterministic local routing/context/evaluation/feedback/audit calls |
| `/api/export` | GET | brain path + agent prompt |

No shell endpoint. No arbitrary filesystem access.

## Security

- localhost-only by default; a non-local host refuses to start without `CATALYST_TOKEN`
- no shell or exec endpoint of any kind
- no arbitrary filesystem access: every path is resolved and must stay inside an allowlisted repo-relative root
- reads limited to `outputs/`, `templates/`, `docs/`, `prompts/`, and fixed repo metadata/status endpoints
- writes limited to `outputs/` and fixed local config files under `.catalyst/`
- `templates/` are never written
- BYOK keys are env-only and never returned to the browser

## Legacy panel

The old vanilla staged panel remains available at `/legacy/` as an archived/dev fallback. Public docs should describe the React UI at `/` as the canonical local command center.

## Hosted path

Local UI = free local engine.

Hosted Catalyst later = synced/no-setup/always-on Catalyst across agents. The local CTA points to `https://itscatalyst.com` and founding install email only. No Stripe, accounts, or hosted backend exist in this repo.
