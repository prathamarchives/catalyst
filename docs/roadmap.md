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

## v0.3 — first-dollar install kit

Manual paid install offer around building a user's Catalyst Brain and making their AI stop resetting across sessions.

## later

Only after repeated manual proof and real demand: a heavier web app (`apps/web`), a hosted option, or an MCP surface. These stay optional layers on top of the same local protocol — never required infrastructure, never a hosted-by-default rewrite.
