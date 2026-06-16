# product surface — landing source of truth

This file is the canonical copy for a landing page or repo homepage. Keep it concrete. No launch hype.

## One line

Creed helps agents remember you. Catalyst teaches agents what you'd approve, reject, revise, and remember.

## The 30-second version

- **What it is:** a local-first, markdown-first judgment system for agents. It turns your messy source material — AI sessions, notes, drafts, rejected outputs, corrections — into a multi-file **Catalyst Brain** an agent loads before work, reviews against after work, and updates every time you correct it.
- **How it differs from one-file context/profile tools:** a profile file makes an agent remember facts about you. Catalyst makes an agent *judge* a specific output against your standards, reject what you'd reject, and improve from feedback. Memory is flat; judgment is task-time.
- **How you run it locally:** clone/open the repo, point an agent at `AGENTS.md`, or run the optional control panel with `py apps/control-panel/server.py`. No account, no database, no hosted backend.
- **What the UI / onboarding does:** asks 5–7 questions, runs read-only source discovery, gets your approval for any scan, builds the brain under `outputs/<name>/`, runs a first proof task, and updates the brain from your feedback.
- **How it stays private:** local files only; discovery is read-only path metadata; reading contents needs your approval; secrets/DMs/client data excluded by default; outputs are gitignored; no cloud upload by default.
- **How BYOK is optional:** everything core works with no key (mock mode, no network). A key only powers optional AI-assisted synthesis/review.
- **How feedback makes agents improve:** every correction becomes a feedback-memory entry plus a patch to standards/judgment/taste plus a new eval line. The next task inherits the rule.

## What it is not

- not voice cloning or "AI that writes like you"
- not a single context/profile file
- not a hosted memory app or SaaS
- not a content pipeline or scheduler

## The loop (the actual product)

```txt
task → load relevant brain files → produce → review against standards/judgment/identity
     → revise if it misses → show you → capture feedback → patch brain/skills/evals → sharper next task
```

The proof is not a staged before/after. The proof is that the agent gets harder to disappoint over time.

## Who it's for

People who run agents on real work — coding, writing, research, business, creative — and are tired of re-explaining their standard every session and re-rejecting the same slop.
