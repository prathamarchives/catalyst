# REPO-USE-PROMPT — copy/paste this to your agent

Open this repo with your agent, then paste the variant that matches your setup. Every variant carries the same core instruction: discover first, ask for approval, then build the Creative Brain.

## Install from a link (start here)

If you're starting from scratch, the shortest path is to give your agent the repo link and one prompt. Use the **autonomous one-shot** when your agent can read files and run code — it pre-authorizes the safe scan so the agent runs end to end without stopping to ask again:

```txt
https://github.com/prathamarchives/catalyst
install this and build my Creative Brain.
You may discover and scan my local AI sessions, agent memories, workspaces, markdown notes, and project files using the recommended safe scope.
Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and anything sensitive.
Build everything locally, write the personalized skill/workflows/evals, run a before/after proof, then ask me for taste feedback and update the brain.
```

Prefer to approve the scope first? Use the cautious one-liner instead:

```txt
https://github.com/prathamarchives/catalyst
help me install this and build my Creative Brain
```

This is a protocol repo, not an app — there is no package install, and a correct agent does not stop at clone. It clones/opens, confirms no package step is needed, then runs setup: discover sources → recommend a safe scan scope → (autonomous authorized mode proceeds; cautious approval mode asks one approval question) → build the brain. See [INSTALL.md](INSTALL.md) for the full flow and [SETUP-PROMPT.md](SETUP-PROMPT.md) for autonomous / cautious / manual copy-paste versions. The variants below are for driving individual agents directly.

## Core prompt (any agent)

```txt
Read README.md and AGENTS.md. Use this repo to build my Creative Brain.
First discover where my AI sessions, notes, exports, and workspaces live. Do not read file contents yet.
Show me the discovered locations, ask what you may scan, then audit only the approved scope.
Interview me in small rounds, create files under outputs/<name>/, write a catalyst skill, run a before/after proof, then ask for feedback and update the system so it compounds session to session.
```

Replace `<name>` with your name or project, or let the agent ask you.

## Claude Code

Open a terminal in this repo and run `claude`, then paste:

```txt
Read README.md and AGENTS.md in this repo and follow the protocol exactly.
You are building my Creative Brain. Your first action: run tools/discover_sessions.py or replicate its logic to discover candidate AI sessions, notes, exports, and project workspaces across my machine. Do not read contents yet.
Show me the discovered list grouped by source and ask which locations I approve for scanning.
After approval, audit only that scope, interview me in small rounds (max 3-4 questions at a time), extract voice/taste/context/judgment/behavior with evidence quotes, create all files under outputs/<name>/, write my catalyst-skill.md, run the before/after proof from prompts/06, then ask for my feedback and update feedback-memory.md and the skill from it.
```

## Cursor

Open this repo as a workspace, open the agent panel, and paste:

```txt
Read README.md and AGENTS.md and execute the protocol in AGENTS.md step by step.
Build my Creative Brain. Start by discovering candidate sources across the system — Cursor/VS Code storage, Claude/ChatGPT exports, CLI agent sessions, notes, and workspaces — then show me the scope and ask what you may scan.
Do not write any final content yet. Audit approved sources, interview me in small rounds, extract with evidence quotes, build the ten creative-brain files under outputs/<name>/, write the catalyst skill, run the before/after proof, then collect my feedback and update the brain and skill from it. Never modify anything under templates/.
```

## Hermes

Point Hermes at this repo (or paste the repo path) with:

```txt
This repo is an agent protocol: read README.md and AGENTS.md, then run the catalyst protocol on me.
Start by discovering where my past sessions, notes, exports, and workspaces live. Show me the discovered locations and ask what you may scan before reading contents.
Build the Creative Brain under outputs/<name>/, write the skill, run the before/after proof, then fold my feedback into feedback-memory.md so the system compounds session to session.
```

## Any generic agent

If your agent can read files and write files, paste the core prompt at the top of this page. If it can run Python, have it run `tools/discover_sessions.py` first. If it cannot run tools, paste the contents of `AGENTS.md` and `prompts/00-start-here.md` directly into the chat, then manually supply the source locations it should scan.

## What to expect

1. The agent discovers candidate source locations and shows them to you.
2. You approve the scan scope. It reads only approved locations.
3. It audits, then interviews you in short rounds.
4. It builds `outputs/<name>/creative-brain/` (ten files), a skill, and workflows.
5. It runs one task twice — without and with your brain — and shows you both.
6. You react. It turns your reactions into durable memory and patches the brain/skill.

If the agent starts generating content before your brain exists, stop it and point it back to AGENTS.md.
