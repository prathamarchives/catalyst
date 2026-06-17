# roadmap

## v0 — Catalyst Brain protocol

Markdown-first local protocol: discovery, permission, audit, extraction, Catalyst Brain, skills, task-time evaluation, feedback update, and memory lifecycle.

## v0.1 — stronger generated skills

Better task routing, quick/full modes, standards review, feedback capture, and file-specific update rules.

## v0.2 — local control panel, guided onboarding, optional BYOK

Make the protocol understandable and operable without losing local-first:

- README clarity: judgment vs one-file context tools, made explicit.
- Guided onboarding (5–7 questions) that builds a seeded brain under `outputs/<name>/` before any scan.
- Optional zero-dependency local control panel (Python stdlib + vanilla JS): status, onboarding, source approval, brain explorer/editor, proof, BYOK, export. Localhost-only, allowlisted file ops.
- Optional BYOK provider abstraction with a mock/no-key mode that always works; keys live in env only.
- Export guides so the same brain runs in Claude Code, ChatGPT exports, Cursor, Hermes, Codex.

The control panel is an optional surface, not the product. The markdown protocol stays the source of truth and runs with no UI and no key.

## v0.3 — agent-native onboarding + MCP scaffold

Sharpen the control panel into a staged, Apple-inspired setup journey and make it agent-native:

- one coherent flow: Start → Connect AI → Identity → Context → Permission → Build → Explore → Proof → Agents (MCP).
- **connect an AI/agent first** — mock/offline, OpenRouter BYOK, detected CLIs (Claude Code/Codex/Hermes, existence-only), and a manual-prompt fallback. Honest status; mock is never shown as live.
- context import: paste a dump, name manual paths, or run the extraction prompt through any LLM and paste the packet back; saved under `outputs/<name>/sources/`. No fake Notion/Slack/Discord OAuth — connectors are labeled export/drop/paths.
- honest staged build, grouped brain explorer, proof loop that contrasts memory vs judgment.
- `tools/mcp_server.py`: dependency-free, local-only MCP scaffold exposing `list_brain_sections`, `read_brain_section`, `review_output_against_brain`, `append_feedback`, `propose_brain_update`. Writes only via feedback/proposal; never overwrites the brain.

## v0.4 — local app (judgment backend + UI + MCP)

The runnable engine and the consumer flow, one path. `catalyst_core/` runs route → context (+ agent judgment contract) → evaluate → feedback → proposal → audit/distill. One launcher (`py catalyst.py`) starts the local server and opens the browser; one onboarding flow extracts and imports context into the brain; the agent connects once over MCP and then reads/writes/evaluates/improves every task. The dev CLI, `/api/flow/*`, and MCP all share one engine. See [docs/catalyst-flow.md](catalyst-flow.md) and [docs/architecture.md](architecture.md).

## v0.5 — first-dollar install kit

Manual paid install offer around building a user's Catalyst Brain and making their AI stop resetting across sessions.

## later

Only after repeated manual proof and real demand: a hosted option and packaged installers so non-developers skip `git clone`. These stay optional layers on top of the same local-first app — never required infrastructure, never a hosted-by-default rewrite.
