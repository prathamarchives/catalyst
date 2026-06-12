# SETUP-PROMPT — copy/paste this to your agent

Three versions. Pick the one that matches how much you trust your agent and how much code it can run. All three reach the same place: a Creative Brain under `outputs/<name>/` with no path-management busywork on you.

If you only remember one sentence, it's this:

```txt
https://github.com/prathamarchives/creative-identity
help me install this and build my Creative Brain
```

A correctly-behaving agent does the rest, pausing only for scope approval and taste feedback.

---

## 1. Full autonomous (local agent, can run code)

For Claude Code, Cursor, Hermes, or any agent that can run Python and read/write files on your machine.

```txt
Clone/open this repo: https://github.com/prathamarchives/creative-identity
Read INSTALL.md, README.md, AGENTS.md, and REPO-USE-PROMPT.md.
Confirm no package install is needed — this is a protocol repo, not an app. Do not stop at clone.
Run the evals if allowed (py evals/run_all.py); if blocked, say so and continue — verification is optional.
Then follow prompts/08-install-and-run.md:
- Discover candidate source locations with tools/discover_sessions.py (read-only).
- Recommend a safe scan scope. Do not dump a folder list at me.
- Ask me ONE approval question: approve recommended scan / edit scope / manual mode.
- Scan only the approved scope. Inventory before deep reading. Prioritize rejected outputs and feedback.
- Build my Creative Brain under outputs/<name>/ (ten creative-brain files).
- Write my customized creative-identity-skill.md.
- Copy all five workflows into outputs/<name>/workflows/.
- Initialize outputs/<name>/evals/blind-ab-log.md.
- Run the before/after proof (prompts/06). Run the blind A/B proof (prompts/10) when possible.
- Ask me for feedback, then update feedback-memory.md, the affected brain files, and the skill.
- Set up a memory distillation cadence (prompts/09).
- Hand off with exact instructions for how I load the brain next time.
Only interrupt me for: scan-scope approval, small interview gaps, taste feedback, and any destructive or external action.
```

---

## 2. Cautious, permission-gated (review each major step)

For when you want to approve actions as they happen, or your agent runs in a restricted environment.

```txt
Clone/open https://github.com/prathamarchives/creative-identity and read INSTALL.md + AGENTS.md.
This is a protocol repo — confirm no package install is needed, but do not stop at clone.
Work through prompts/08-install-and-run.md and pause for my OK before each of these:
1. running any code (evals, discovery helper)
2. reading any source files (show me the recommended scan scope first; I approve, edit, or switch to manual)
3. writing the outputs/<name>/ folder
After each gate, proceed only with what I approved. Never read beyond the approved scope.
Then build the brain, write the skill, copy workflows, init the blind A/B log, run the before/after proof,
collect my feedback, and update feedback-memory + the skill. Tell me the distillation cadence at the end.
```

---

## 3. No-code / manual fallback (agent can't run tools, or you prefer to drive)

For chat-only agents, or when you'd rather hand over files yourself.

```txt
This repo is an agent protocol. Read AGENTS.md and prompts/00-start-here.md (I'll paste them if you can't open files).
No package install is needed; this is markdown, not an app.
Skip the discovery script. Instead, I'll tell you where my material is: I'll paste or point you to my exported
Claude/ChatGPT conversations, notes, drafts, posts, and especially AI outputs I disliked and why.
From only what I give you: extract voice/taste/judgment/behavior with evidence quotes, build the ten
creative-brain files (I'll save them under outputs/<name>/), write my skill, run a before/after proof on one
real task, then take my feedback and turn it into durable rules in feedback-memory.md.
Don't write my content before the brain exists. Ask me in small rounds, not all at once.
```

---

## what to expect either way

1. Agent clones/opens the repo and tells you install is complete (no package step).
2. Agent discovers source locations and recommends a safe scan scope — one approval question.
3. You approve (or edit, or go manual). It reads only what you approved.
4. It builds `outputs/<name>/` — brain, skill, workflows, blind A/B log.
5. It runs one real task twice (without and with your brain) and shows you both.
6. You react. It turns reactions into durable memory and patches the brain + skill.
7. It tells you the distillation cadence and how to load the brain next session.

If the agent stops after cloning, or asks you to find your own session paths, point it back to [INSTALL.md](INSTALL.md) and [prompts/08-install-and-run.md](prompts/08-install-and-run.md).
