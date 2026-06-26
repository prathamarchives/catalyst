# MCP + multi-agent access

Catalyst exposes the local brain to agents through a small, allowlisted server so
many agents can **retrieve, evaluate, and evolve** the same brain — without giving
them raw filesystem access.

Status: **scaffold, honestly.** `tools/mcp_server.py` is a dependency-free
JSON-RPC 2.0 stdio server that implements the core MCP methods (`initialize`,
`tools/list`, `tools/call`) plus the Catalyst file tools and Persona Brain
runtime tools. It is local-only and makes
no network calls. It is a working scaffold, not a certified MCP build verified
against every client's handshake. Treat it as the boundary, not the finished product.

## Run

```txt
py tools/mcp_server.py
```

It reads JSON-RPC requests on stdin and writes responses on stdout. An MCP client
connects by launching that command as a stdio server.

## Tools (allowlisted)

| tool | access | what it does |
|------|--------|--------------|
| `list_brain_sections` | read | section index grouped by job |
| `read_brain_section` | read | one brain file's markdown |
| `route_task` | read | classify a task and return the brain files to load |
| `get_context_packet` | read | full context packet (identity/standards/judgment/taste + judgment contract) |
| `review_output_against_brain` | read | deterministic evaluation: verdict (ship/revise/reject/ask) + 0–5 scores + issues |
| `audit_brain` | read | readiness score + thin/stale/duplicate flags + distill recommendation |
| `append_feedback` | write | capture a correction: append `feedback-memory.md` + `improvement-log.md` and write a review proposal |
| `propose_brain_update` | write | write a PROPOSAL under `proposed-updates/` — never overwrites the brain |

All file-brain tools take a `name` (the brain under `outputs/<name>/`).

Runtime tools use local `.catalyst/` state and do not require an existing
`outputs/<name>/` brain:

| tool | access | what it does |
|------|--------|--------------|
| `catalyst_recall` | read/write log | context packet before work |
| `catalyst_capture` | write | event -> signals -> memories -> graph -> compiled Persona Brain |
| `catalyst_search` | read | search memory atoms |
| `catalyst_profile` | read | compact memory profile grouped by sub-brain |
| `catalyst_review` | read/write log | review output against recalled memory and local quality rules |
| `catalyst_health` | read/write log | event, signal, memory, sub-brain, graph, orphan, and dead-link health |
| `catalyst_graph` | read | machine graph and summary |
| `catalyst_propose_update` | write | local proposal record, never applied silently |

## Security boundary

- read access is limited to `outputs/<name>/catalyst-brain/*.md`
- the only write paths are `append_feedback` (→ `feedback-memory.md`, `evals/improvement-log.md`, and a dated proposal under `proposals/`) and `propose_brain_update` (→ `proposed-updates/`), all confined to `outputs/`
- no arbitrary path access (traversal rejected), no shell, no network
- the brain is never silently overwritten — updates land as proposals for review

## Connecting agents

These are connector *instructions*, not live OAuth. Point each client at the stdio command above.

- **Claude Code** — add an MCP server entry whose command is `py tools/mcp_server.py` (cwd = repo root). The local UI exposes the copyable `claude mcp add ...` command when useful.
- **Cursor** — add a custom MCP server with the same command in its MCP settings.
- **Hermes / Codex / OpenAI-style agents** — launch the command as a stdio MCP server, or call the same Python functions directly (`from tools import mcp_server`).
- **Generic MCP client** — stdio transport, command `py tools/mcp_server.py`.

If your client cannot speak MCP yet, agents can still use the brain directly: read
`outputs/<name>/catalyst-brain/*.md` and follow `AGENTS.md`. The MCP layer is an
optional convenience, not required infrastructure.

During setup, the connected agent is the builder. It should read `.catalyst/permissions.json`, run read-only discovery, build under `outputs/<name>/`, and keep `outputs/<name>/BUILD-STATUS.json` updated so the local UI can render progress.

## What's next

- verify the handshake against the official MCP Python SDK and add it as an optional dependency if it justifies itself
- a thin HTTP transport for clients that prefer it (still local-only)
- an apply-with-approval path that turns accepted proposals into real brain patches via the update workflow
