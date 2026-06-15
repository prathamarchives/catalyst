# 01 — source audit

Goal: find high-signal material and route it into the right Catalyst Brain files.

## Discover first

Check candidate locations for `.claude`, Claude Code projects, Cursor/VS Code state, Hermes memory, ChatGPT exports, Claude exports, Notion/Obsidian exports, markdown notes, and workspaces. Discovery only checks paths; it does not read contents.

## Authorization

Recommended scan: AI sessions + exports + agent memories + markdown-heavy workspaces. Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and anything sensitive.

## Audit dimensions

For each approved source, extract candidate evidence for:

- identity: who/what the agent represents
- context: current work, people, projects, constraints
- goals: desired outcomes and priorities
- constraints: limits, boundaries, non-negotiables
- standards: quality bar and success/failure criteria
- judgment: decision rules, approvals/rejections, pushback patterns
- taste: examples, references, cultural standards
- voice: language, rhythm, phrases, not the whole product
- anti-slop: repeated weak patterns
- rejected examples: killed outputs and why
- decision-rules: when to choose, wait, push, cut, ship
- task-patterns: recurring task types and expected handling
- feedback-memory: corrections and their durable rules
- open-questions: uncertain assumptions

Rejected examples and corrections outrank generic banned-word lists because they show the standard by contrast.
