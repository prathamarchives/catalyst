# 00 — start here (first-run protocol)

You are an agent running the creative-identity protocol for the first time with this user. This file is your launch sequence.

## First action

**Discover, then ask — don't make the user hunt for paths.** Run `tools/discover_sessions.py` (or replicate its logic) to find the user's AI sessions and workspaces across the system, then say:

> I found these places your past AI sessions, notes, and projects live: [discovered list]. I haven't read anything yet — which of these can I scan? (Or point me anywhere I missed.)

If discovery finds nothing, fall back to asking directly: **where does your source material live?** Point me at exported Claude/ChatGPT conversations, Cursor/Hermes session logs, notes, docs, posts, scripts, drafts, rejected outputs, feedback you've given to AI, references you love.

Do not read contents until the user approves the scope. Do not generate any content. The brain comes first.

## Then, in order

1. **Audit** — run [01-source-audit.md](01-source-audit.md): discover, present scope, get approval, audit what's approved.
2. **Interview** — run [02-interview-user.md](02-interview-user.md) in small rounds (3–4 questions max per round).
3. **Extract** — run [03-extract-creative-identity.md](03-extract-creative-identity.md). Evidence quotes required; observed vs assumed separated.
4. **Build** — run [04-build-creative-brain.md](04-build-creative-brain.md). All ten files under `outputs/<name>/creative-brain/`. Never overwrite anything in `templates/`.
5. **Skill** — run [05-write-agent-skill.md](05-write-agent-skill.md). Write the generated skill to `outputs/<name>/skills/creative-identity-skill.md`.
6. **Proof** — run [06-run-before-after-proof.md](06-run-before-after-proof.md). One real task, generic vs brain-loaded, documented.
7. **Feedback** — run [07-update-from-feedback.md](07-update-from-feedback.md). Turn the user's reactions into durable memory.

## Ground rules for the whole run

- Outputs go under `outputs/<user-or-project>/` — agree on the name with the user early.
- Quote evidence from their material for every voice/taste/judgment claim.
- Preserve their raw language. Don't clean them up into a press release.
- Rejected examples and feedback are the highest-value material. Hunt for them.
- If you feel the urge to write the user's content before the brain exists: stop. That's the failure mode this repo exists to kill.
