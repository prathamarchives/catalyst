# catalyst

A local protocol for giving agents identity, judgment, standards, and adaptive feedback.

Catalyst turns messy source material — AI sessions, notes, drafts, rejected outputs, project files, and user corrections — into a **Catalyst Brain** your agent can load before it works, review against after it works, and update every time you correct it.

Not voice cloning. Not a content pipeline. Not a hosted memory app.

```txt
source material → Catalyst Brain → task routing → standards review → feedback capture → brain/skill/eval update → sharper next task
```

The goal is: the agent knows who it represents, what standard the work must meet, how to judge outputs, what the user rejects, and how to improve from every task instead of resetting every session.

## Start here

Paste this into Claude Code, Cursor, Hermes, or any agent that can read/write local files:

```txt
https://github.com/prathamarchives/catalyst
install this and build my Catalyst Brain.
You may discover and scan my local AI sessions, agent memories, workspaces, markdown notes, and project files using the recommended safe scope.
Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and anything sensitive.
Build everything locally, write the personalized skills/workflows/evals, run the first real task through the task-time evaluation loop, then ask me for feedback and update the brain.
```

Prefer approval first? Use:

```txt
https://github.com/prathamarchives/catalyst
help me install this and build my Catalyst Brain
```

Full install model: [INSTALL.md](INSTALL.md). Copy/paste prompts: [SETUP-PROMPT.md](SETUP-PROMPT.md). Direct agent prompt: [REPO-USE-PROMPT.md](REPO-USE-PROMPT.md).

## What this repo is

`catalyst` is a markdown-first, local-first, agent-runnable protocol. It provides:

- [AGENTS.md](AGENTS.md): the operating protocol an agent executes
- [prompts/](prompts/): modular steps for discovery, audit, extraction, build, skills, task evaluation, feedback, and distillation
- [templates/catalyst-brain/](templates/catalyst-brain/): the generated brain structure
- [templates/skills/](templates/skills/): future-agent instructions that make the brain usable
- [templates/workflows/](templates/workflows/): task, review, update, and distillation loops
- [templates/evals/](templates/evals/): standards checks and improvement logs
- [tools/discover_sessions.py](tools/discover_sessions.py): read-only discovery helper
- [evals/](evals/): static checks that keep the repo coherent

There is no package install, account, visual control panel, database, API key, or hosted service. “Install” means clone/open the repo, verify it if possible, and let an agent build the local Catalyst Brain under `outputs/<name>/`.

## What it creates

```txt
outputs/<name>/
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

## Run evals

```txt
python evals/run_all.py
py evals/run_all.py
```

Exit code 0 means the repo structure, protocol completeness, privacy language, output consistency, and task-time improvement loop are coherent.
