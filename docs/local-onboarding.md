# local onboarding

Guided onboarding gets a usable Catalyst Brain on disk fast, without making the user hunt for paths and without reading anything they didn't approve. It runs two ways: as an agent following `AGENTS.md`, or through the optional control panel (`apps/control-panel/`). Both produce the same local files under `outputs/<name>/`.

## Principle

Connect an AI first, ask little, build locally, prove on real work. The brain is seeded from the user's typed answers and imported context first; deeper material comes only from sources the user approves and a connected model/agent to synthesize them.

## Connect an AI / agent first

Before identity questions, the flow establishes how this session does real work. Without a connected model or agent, Catalyst can only copy empty templates — synthesis, evaluation, and updates need a worker.

Modes, offered honestly by status:

- **Mock / offline** — always available, no network, deterministic placeholder. Demo only.
- **OpenRouter BYOK** — real synthesis on approved text; key from env only (`OPENROUTER_API_KEY`).
- **Claude Code / Codex / Hermes CLI** — detected via `shutil.which` (existence only; login state unknown; v0.3 does not execute them for you).
- **Manual LLM prompt** — always available; copy a prompt into any LLM and paste the result back. Best no-key path to real synthesis.

The UI must never imply a live model exists when only mock is available.

## The 5–7 questions (max)

Ask these before any scanning or building:

1. **Name/handle** — what should this Catalyst Brain represent? (becomes `outputs/<name>/`)
2. **Main use** — what are you mainly using agents for right now? coding / writing / research / business / creative / other
3. **Never ship** — what should agents never ship in your name? (the instant-reject lines)
4. **Approved work** — what examples count as approved work or good taste? (links, snippets, descriptions)
5. **Rejected work** — what examples or corrections show rejected work or slop? (highest signal — the standard shows up by contrast)
6. **Sources** — what local sources may Catalyst inspect? recommended safe scan / manual paths / skip scan
7. **First proof task** — what is the first real task to use as proof?

Keep it to small rounds. Do not dump 40 interview questions.

## Flow

1. **Connect AI** — establish the session's worker (mock / BYOK / detected CLI / manual prompt). See above.
2. **Welcome + collect answers** — local-first in plain language, then the 5–7 above.
3. **Context import** — instead of an endless interview, let the user paste a context dump, name manual paths, or run the extraction prompt through any LLM and paste the structured packet back. Saved under `outputs/<name>/sources/`. Nothing is read from disk yet.
4. **Read-only discovery** — run `tools/discover_sessions.py` (or the panel's Permission step). This checks where AI sessions, notes, exports, and workspaces live. It reads no file contents — path metadata only.
5. **Recommend safe scope** — show discovered *categories*, not giant path dumps. Recommend the safe preset (AI sessions, notes, markdown workspaces; exclude secrets/tokens/private DMs/client data/vendor/build/binaries).
6. **Approval gate** — if the starting prompt already authorized a recommended safe scan, proceed (autonomous authorized mode). Otherwise ask exactly one compact approval question: *approve recommended scan, edit scope, or skip?*
7. **Scan approved scope only** — read contents only inside what was approved. Exclusions always bind.
8. **Generate the brain** — create `outputs/<name>/catalyst-brain/` plus `skills/`, `workflows/`, `evals/` from `templates/`. Seed `identity/goals/constraints/taste/rejected-examples/task-patterns` with the answers and imported context as observed evidence. With a live provider, synthesize on approved text; with no key, write a clearly-labeled mock/no-key seed.
9. **Run the first proof task** — take it through the task-time evaluation loop (`prompts/06-task-time-evaluation.md`): load relevant files, produce, review against standards, show the user.
10. **Capture feedback and update** — route the reaction into `feedback-memory.md` and patch the right brain/skill/eval (`prompts/07-update-from-feedback.md`).

## Context extraction prompt

The panel and `apps/control-panel/server.py` expose a copyable prompt that tells any LLM to extract identity, goals, projects, constraints, standards, judgment rules, approved examples, rejected examples, voice/taste, workflows, recurring corrections, open questions, and sources/evidence as structured markdown for Catalyst ingestion. Paste your context into it, run it in any model, paste the result back at the Context step.

## In the control panel

The flow connects AI first, then collects identity, then imports context, then runs read-only discovery and the one approval question, then builds. The Build step shows honest staged progress; the Proof step runs the first task-time review. See [docs/control-panel.md](control-panel.md).

## Privacy

Discovery is read-only. Content scanning is authorized. Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, dependency folders, and sensitive material. Outputs are gitignored. A hosted model/provider may receive approved context — only matters if you enable BYOK or run inside a hosted agent. See [docs/privacy.md](privacy.md) and [docs/permission-model.md](permission-model.md).
