# Architecture

Catalyst is a local-first app. A small Python server serves a prebuilt UI and a local
API, the brain stays as markdown under `outputs/<name>/`, and one engine (`catalyst_core/`)
powers every surface. No accounts, no cloud, no database.

```
┌─ apps/web (React/Vite, built → dist/) ──────────────┐
│  Onboarding (welcome→extract→import→review→connect)  │
│  Workspace (brain view, activity, readiness, MCP)    │
└───────────────▲──────────────────────────────────────┘
                │ fetch /api/*   (localhost only)
┌───────────────┴── apps/control-panel/server.py ──────┐
│  serves dist/ (or the legacy panel) + auto-opens      │
│  /api/flow/route|context|evaluate|feedback|audit      │
│  /api/import/discover|files|extract                   │
│  /api/onboarding, /api/brain, /api/file (existing)    │
│  security: 127.0.0.1, allowlist, writes ⊂ outputs/    │
└───────┬───────────────────────────────────┬──────────┘
        │ import                              │ import
┌───────▼── catalyst_core/ ─────┐   ┌─────────▼ tools/mcp_server.py ┐
│ paths registry router contract│   │ route_task get_context_packet │
│ packet evaluator feedback     │◄──┤ review_output_against_brain   │
│ quality   (the judgment engine)│  │ append_feedback audit_brain   │
└───────┬───────────────────────┘   │ propose_brain_update …        │
        │ read/write                 └───────────▲───────────────────┘
┌───────▼── outputs/<name>/ (LOCAL MARKDOWN BRAIN) ─┐    │ stdio JSON-RPC
│ catalyst-brain/*.md  sources/  proposals/  evals/ │    │
└───────────────────────────────────────────────────┘   └── your AI agent
```

## One engine, three surfaces

The HTTP API, the MCP server, and the dev CLI are thin layers over `catalyst_core` —
no duplicated logic. Add a capability once in the engine and all three gain it.

## Local-first / security boundaries (preserved)

- Server binds `127.0.0.1`; a non-local bind requires `CATALYST_TOKEN`.
- No shell/exec endpoint; no arbitrary filesystem access — every path is resolved against an allowlist.
- Writes are confined to `outputs/`; `templates/` are never written.
- Core brain rule files are never silently mutated — feedback is append-only and edits land as review proposals.
- BYOK keys stay server-side and are never returned to the browser.

## Why local markdown is the substrate, not the moat

The brain stays human-readable markdown so it is portable and yours. The moat is the
**judgment loop** — routing, the agent judgment contract, evaluation, and compounding —
not the file format.
