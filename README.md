# catalyst

A local app/runtime for giving agents identity, context, taste, judgment, standards, and adaptive feedback.

Catalyst turns messy source material — AI sessions, notes, drafts, rejected outputs, project files, and user corrections — into a **Catalyst Brain** your agent can load before it works, review against after it works, and update every time you correct it.

Not voice cloning. Not a content pipeline. Not a hosted memory app.

```txt
source material → Catalyst Brain → task routing → standards review → feedback capture → brain/skill/eval update → sharper next task
```

The goal is: the agent knows who it represents, what standard the work must meet, how to judge outputs, what the user rejects, and how to improve from every task instead of resetting every session.

## Catalyst vs one-file context tools

One-file context tools help agents remember who you are.
Catalyst teaches agents what you would approve, reject, revise, and remember.

Catalyst is for people who do not just need more memory. They need agents that can judge work against their standards, learn from corrections, and get harder to disappoint over time.

The difference is depth, not branding:

- **Memory / profile** — a single context file is useful but flat. It tells an agent facts about you. It does not tell the agent what "good" means for a specific task, or what you would reject.
- **Judgment** — task-time standards, rejected examples, approval logic, and feedback updates. This is the part that changes the output, not just the agent's self-description.
- **A multi-file local brain** — identity, standards, judgment, taste, rejected examples, decision rules, task patterns, and feedback memory live in separate files an agent loads by task, not one blob.
- **The proof is the loop** — `task → load brain → produce → review against standards → show you → capture feedback → update brain/skill/eval`. The agent gets harder to disappoint over time because every correction becomes an operational rule.

This is early and honest about it: Catalyst is a local runtime plus an agent protocol, not a finished hosted service. The value is the loop, run on real work.

## Start here

One-command local app path:

```txt
npx catalyst local
```

Until the unscoped package exists, use the scoped launcher:

```txt
npx @trycatalyst/cli local
```

Local development from this checkout:

```txt
node packages/cli/bin/catalyst.mjs local --repo <path-to-this-repo>
```

The command opens a localhost command center. First screen: connect your agent. The agent is the v0 builder; the local UI is the command center and brain viewer.

Paste this into Claude Code, Cursor, Hermes, or any agent that can read/write local files:

```txt
https://github.com/prathamarchives/catalyst
install this and build my Catalyst Brain.
You may discover and scan my local AI sessions, agent memories, workspaces, markdown notes, and project files using the recommended safe scope.
Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and anything sensitive.
Build everything locally, write BUILD-STATUS.json while you work, write the personalized skills/workflows/evals, then install the task-time evaluation and feedback update loop for future real tasks.
```

Prefer approval first? Use:

```txt
https://github.com/prathamarchives/catalyst
help me install this and build my Catalyst Brain
```

Full install model: [INSTALL.md](INSTALL.md). Copy/paste prompts: [SETUP-PROMPT.md](SETUP-PROMPT.md). Direct agent prompt: [REPO-USE-PROMPT.md](REPO-USE-PROMPT.md).

## What this repo is

`catalyst` is a local-first, agent-runnable runtime with human-readable markdown under the hood. It provides:

- [AGENTS.md](AGENTS.md): the operating protocol an agent executes
- [prompts/](prompts/): modular steps for discovery, audit, extraction, build, skills, task evaluation, feedback, and distillation
- [templates/catalyst-brain/](templates/catalyst-brain/): the generated brain structure
- [templates/skills/](templates/skills/): future-agent instructions that make the brain usable
- [templates/workflows/](templates/workflows/): task, review, update, and distillation loops
- [templates/evals/](templates/evals/): standards checks and improvement logs
- [tools/discover_sessions.py](tools/discover_sessions.py): read-only discovery helper
- [catalyst_core/](catalyst_core/): hybrid brain models, markdown parser/manager, routing, context assembly, evaluator, feedback processor, proposals, version history, retrieval, health, and runtime state
- [tools/mcp_server.py](tools/mcp_server.py): local MCP scaffold with brain context, evaluation, feedback capture, proposals, section listing, health, and compatibility tools
- [evals/](evals/): static checks that keep the repo coherent

There is no required package install, no account, no database, no required API key, and no hosted service. An optional local control panel ships in `apps/control-panel/` (Python standard library, localhost-only) and an optional BYOK helper exists, but the protocol runs fully without either. “Install” means clone/open the repo, verify it if possible, and let an agent build the local Catalyst Brain under `outputs/<name>/`.

## What it creates

```txt
outputs/<name>/
  BUILD-STATUS.json
  SUMMARY.md
  catalyst-brain/
    README.md
    identity.md
    context.md
    goals.md
    constraints.md
    standards.md
    judgment.md
    taste.md
    voice.md
    anti-slop.md
    references.md
    rejected-examples.md
    decision-rules.md
    task-patterns.md
    feedback-memory.md
    lexicon.md
    open-questions.md
  skills/
    catalyst-skill.md
    use-catalyst-brain.md
    update-catalyst-brain.md
    review-against-standards.md
    extract-feedback.md
    task-routing.md
    distill-memory.md
  workflows/
    start-task.md
    produce-output.md
    review-output.md
    update-after-feedback.md
    weekly-distillation.md
  evals/
    output-review.md
    standards-check.md
    identity-alignment.md
    judgment-check.md
    feedback-capture.md
    improvement-log.md
  README.md
  proposed-updates/
```

Every brain file includes: purpose, when to load, tasks affected, how to apply, how to update, and what not to put there.

## The core loop

Catalyst is valuable during real use:

1. classify the task
2. load the relevant Catalyst Brain files
3. produce the work
4. review the output against standards, judgment, identity, and task patterns
5. show the user
6. capture explicit and implicit feedback
7. patch the right brain files, skills, and evals
8. log the improvement so the next task benefits

The proof is not a staged comparison. The proof is that the agent gets harder to disappoint over time because every correction becomes an operational rule.

## The hybrid local runtime

The loop is runnable, not just documented. `catalyst_core/` classifies a task, routes the right brain files, builds a compact context packet **with an embedded judgment contract** (how to behave and decide), evaluates output against your standards/judgment/taste, turns feedback into structured proposals, and snapshots accepted updates.

It also includes local runtime state:

```txt
recall -> work -> capture -> extract -> update -> compile -> recall
```

Captured events are stored under `.catalyst/`, extracted into signals, compacted into memory atoms, routed into sub-brains, compiled into a wiki-style Persona Brain, and exposed through health and graph reports. The generated user brain still lives under `outputs/<name>/`; `.catalyst/` is the local runtime state. One launcher starts the local app and opens your browser:

```txt
py catalyst.py
py catalyst.py --no-open
```

The same engine runs over MCP (so your agent does the loop automatically), HTTP APIs, and a dev CLI (`py tools/catalyst_cli.py ...`). See [docs/hybrid-brain-runtime.md](docs/hybrid-brain-runtime.md), [docs/catalyst-flow.md](docs/catalyst-flow.md), [docs/persona-runtime.md](docs/persona-runtime.md), and [docs/architecture.md](docs/architecture.md).

## Privacy model

- local-first: everything is built in files on your machine
- you control the scan: discovery finds candidate paths, but contents are read only inside the scope you approve or pre-authorize
- discovery is read-only and checks candidate locations only; printed local paths are path metadata
- file contents are read only inside the authorized scope
- secrets, tokens, private DMs, client data, vendor/build folders, binaries, and sensitive material are excluded by default
- generated `outputs/**` are gitignored
- review before sharing: read generated files before committing, posting, or sending them anywhere
- no cloud upload by default: this repo itself makes no network calls; your hosted agent/model provider may receive approved context, so do not approve sensitive material unless you understand that tool’s privacy model

Full stance: [docs/privacy.md](docs/privacy.md) and [docs/permission-model.md](docs/permission-model.md).

## Optional local control panel

Catalyst is usable with no UI — point any agent at `AGENTS.md`. If you want a local control surface for the brain, run the zero-dependency panel (Python standard library only, no npm, no build step):

```txt
py apps/control-panel/server.py
python apps/control-panel/server.py
```

Then open `http://127.0.0.1:8765`. It binds localhost only and operates on the real markdown under `outputs/<name>/`. The local UI flow is:

```txt
Promise -> Connect agent -> Source permission -> Build status -> Command center
```

It deliberately connects an agent first. Catalyst needs a worker to discover approved sources, synthesize the brain, and write `outputs/<name>/BUILD-STATUS.json`; the browser only stores permission config and renders local files. Claude Code, Codex, Cursor, Hermes, and manual MCP are offered as honest instructions, not fake live OAuth. Stop the server with Ctrl+C in the terminal. See [apps/control-panel/README.md](apps/control-panel/README.md) and [docs/control-panel.md](docs/control-panel.md).

## Hosted upgrade path

Local Catalyst is the free engine: one machine, local files, manual agent setup. Hosted Catalyst later is the paid convenience layer: synced brains, no local setup, always-on MCP/API, revision history, and multi-agent/team/client workflows.

Want this synced across every agent without local setup? Join hosted Catalyst: [itscatalyst.com](https://itscatalyst.com).

Want a founding install? Email [hello@itscatalyst.com](mailto:hello@itscatalyst.com).

## Multi-agent access (MCP)

`tools/mcp_server.py` is a dependency-free, local-only MCP scaffold (JSON-RPC over stdio) that lets agents call `catalyst_get_brain_context`, `catalyst_evaluate_output`, `catalyst_capture_feedback`, `catalyst_propose_brain_updates`, `catalyst_apply_brain_update`, `catalyst_list_brain`, and `catalyst_get_runtime_health` without raw filesystem access. Older file tools remain as compatibility wrappers. Updates are proposal-backed and never applied silently. It is an honest scaffold, not a certified MCP build. See [docs/mcp.md](docs/mcp.md).

## BYOK is optional

Reading and editing the brain, running the panel, exporting prompts, and using Catalyst manually with an agent all work with **no API key** (a mock provider makes no network calls). A key only powers optional AI-assisted helpers — synthesizing onboarding answers, scoring brain gaps, running a standards review on an output. Keys are read from an environment variable only and never committed. Copy [.env.example](.env.example) to `.env` to enable. See [docs/byok.md](docs/byok.md).

## Run evals

```txt
python evals/run_all.py
py evals/run_all.py
```

Exit code 0 means the repo structure, protocol completeness, privacy language, output consistency, and task-time improvement loop are coherent.
