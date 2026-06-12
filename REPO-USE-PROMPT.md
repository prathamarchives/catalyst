# REPO-USE-PROMPT — copy/paste this to your agent

Open this repo with your agent, then paste the variant that matches your setup. Every variant carries the same core instruction.

## Core prompt (any agent)

```
Read README.md and AGENTS.md. Use this repo to build my Creative Brain.
First ask me where my source material is. Do not generate final content yet.
Audit my sources, interview me in small rounds, create files under outputs/<name>/,
write a creative-identity skill, run a before/after proof, then ask for feedback
and update the system.
```

Replace `<name>` with your name or project, or let the agent ask you.

## Claude Code

Open a terminal in this repo and run `claude`, then paste:

```
Read README.md and AGENTS.md in this repo and follow the protocol exactly.
You are building my Creative Brain. Your first action: ask me where my source
material lives (exported sessions, notes, drafts, posts, rejected outputs, feedback).
Do not generate final content yet. After the audit, interview me in small rounds
(max 3-4 questions at a time). Create all files under outputs/<name>/, write my
creative-identity-skill.md, run the before/after proof from prompts/06, then ask
for my feedback and update feedback-memory.md and the skill from it.
```

## Cursor

Open this repo as a workspace, open the agent panel, and paste:

```
Read README.md and AGENTS.md and execute the protocol in AGENTS.md step by step.
Build my Creative Brain: first ask me where my source material is — do not write
any content yet. Audit sources, interview me in small rounds, extract with evidence
quotes, build the ten creative-brain files under outputs/<name>/, write the
creative-identity skill, run the before/after proof, then collect my feedback and
update the brain and skill from it. Never modify anything under templates/.
```

## Hermes

Point Hermes at this repo (or paste the repo path) with:

```
This repo is an agent protocol: read README.md and AGENTS.md, then run the
creative-identity protocol on me. Start by asking where my source material lives.
Build the Creative Brain under outputs/<name>/, write the skill, run the
before/after proof, then fold my feedback into feedback-memory.md.
```

## Any generic agent

If your agent can read files and write files, paste the core prompt at the top of this page. If it can only read, paste the contents of `AGENTS.md` and `prompts/00-start-here.md` directly into the chat and supply your source material as text.

## What to expect

1. The agent asks where your material lives. Point it at files/folders.
2. It audits, then interviews you in short rounds.
3. It builds `outputs/<name>/creative-brain/` (ten files), a skill, and workflows.
4. It runs one task twice — without and with your brain — and shows you both.
5. You react. It turns your reactions into durable memory.

If the agent starts generating content before your brain exists, stop it and point it back to AGENTS.md.
