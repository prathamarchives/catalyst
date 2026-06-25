# local onboarding

Guided onboarding gets a local Catalyst Brain on disk without making the user hunt for paths and without reading anything they did not approve. It runs two ways: an agent follows `AGENTS.md`, or the optional local UI gives the user copyable agent instructions and a brain viewer.

## Principle

Connect an agent first, ask for scan permission once, build locally, show the brain filling in. The local UI is honest: it does not synthesize the brain by itself in v0. The connected agent is the builder.

## Connect an agent first

Before source scanning, the flow establishes which agent will do real work. Without a connected agent or model, Catalyst can only show prompts and local files.

Modes, offered honestly by status:

- **Claude Code** - CLI detection when available, plus MCP install command and setup prompt.
- **Codex** - CLI detection when available, plus setup prompt.
- **Cursor** - PATH detection when available, plus manual MCP JSON fallback.
- **Hermes** - CLI detection when available, plus setup prompt.
- **Manual MCP** - always available; copy JSON into any MCP client and paste the setup prompt.

The UI must never imply a live hosted connector, OAuth login, or automatic source scan that does not exist.

## Flow

1. **Promise** - Catalyst gives agents taste, context, and judgment.
2. **Connect agent** - user copies one command/prompt for Claude Code, Codex, Cursor, Hermes, or manual MCP.
3. **Source permission** - user chooses recommended safe scan, manual paths only, or skip scan / use typed context. The choice is stored in `.catalyst/permissions.json`.
4. **Agent discovery** - the agent runs `tools/discover_sessions.py` for read-only path metadata. No contents are read yet.
5. **Approval gate** - if `.catalyst/permissions.json` explicitly approves recommended scan, the agent proceeds without a second approval question. If not, it asks one compact approval question: approve recommended scan, edit scope, or manual mode.
6. **Scan approved scope only** - read contents only inside the approved scope. Exclusions always bind: secrets, tokens, private DMs, client data, binaries, vendor/build folders, dependency folders, and sensitive material.
7. **Build the brain** - create `outputs/<name>/BUILD-STATUS.json`, `SUMMARY.md`, `catalyst-brain/`, `skills/`, `workflows/`, `evals/`, and `proposed-updates/`.
8. **Status and graph** - the local UI polls `BUILD-STATUS.json`, shows readiness, missing context, open questions, and a local section graph.
9. **Use with agents** - future tasks load the brain through MCP or direct files. Task-time evaluation and feedback capture run on real work, not as a forced onboarding demo.

## Permission modes

- **Recommended safe scan** - AI sessions, exports, agent memories, markdown-heavy workspaces, and notes. Exclude secrets/tokens/private DMs/client data/binaries/vendor/build/sensitive material.
- **Manual paths only** - only paths the user lists in `.catalyst/permissions.json`.
- **Skip scan / use typed context** - no local content scan; build from pasted context and interview answers.

## Build status

Agents write `outputs/<name>/BUILD-STATUS.json` while building. The local UI renders it and returns safe waiting defaults if it is missing. See `AGENTS.md` for the schema.

## In the control panel

The current screen order is:

```txt
Promise -> Connect agent -> Source permission -> Build status -> Command center
```

The command center shows the active brain name, timeline, graph, readiness, open questions, connected-agent instructions, and hosted/founding CTA. See [docs/control-panel.md](control-panel.md).

## Privacy

Discovery is read-only. Content scanning is authorized. Outputs are gitignored. A hosted model/provider may receive approved context only if you enable BYOK or run the protocol inside a hosted agent. See [docs/privacy.md](privacy.md) and [docs/permission-model.md](permission-model.md).
