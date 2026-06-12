# 01 — source discovery & audit

Goal: find where the user's material lives across the whole system, present the scope, get approval, then audit what's approved — all before reading anything deeply. The user should not have to hunt for paths; that's your job.

## Step 1 — discover (automatic)

Run `tools/discover_sessions.py` (or replicate its logic). It checks known locations across the system and prints the ones that exist. It reads no contents — discovery is not reading.

Locations it covers:

- **Claude Code** — `~/.claude/projects` (per-project session transcripts), `~/.claude.json`, `~/.claude/history.jsonl`
- **Cursor / VS Code** — workspace storage under `%APPDATA%/Cursor` and `%APPDATA%/Code` (chat + composer history)
- **Codex / Copilot / Gemini CLIs** — `~/.codex`, `~/.copilot`, `~/.gemini`
- **ChatGPT / Claude.ai exports** — `~/Downloads` (export zips, `conversations.json`)
- **Notes** — Obsidian vaults, Notion exports
- **Workspaces / projects** — markdown-heavy folders under `~/Desktop` and `~/Documents`

## Step 2 — recommend a scan preset (don't dump paths)

Group what you found and propose a **safe default**, not a list of every folder. Making the user choose among 47 locations is the burden this step exists to remove. Offer three presets:

- **recommended scan:** AI sessions + exports + markdown-heavy workspaces. Exclude secrets, client data, private DMs, binaries, vendor/build dirs.
- **full scan:** all discovered locations, still excluding obvious vendor/build/binary junk.
- **manual:** the user names exact paths.

Add anything the user names that discovery missed (a niche tool, an external drive, a pasted export).

## Step 3 — get approval (one question)

Ask exactly one question, in this shape — not a path-by-path quiz:

> I recommend scanning AI sessions, exports, and markdown-heavy workspaces while excluding secrets/client/private-DM/vendor/build/binary folders. Approve recommended scan, edit scope, or manual mode?

The user approves which locations you may read. Read only what they confirm. **Discovery is automatic; reading is consented.** If they pick manual mode, let them point you at files directly.

## Step 4 — triage, then audit the approved scope

**Inventory before deep reading.** Within the approved scope:

- Prefer `.md`, `.txt`, `.json`, `.jsonl`, `.csv`, chat exports, posts, drafts, feedback, rejected outputs.
- Skip by default: `.git`, `node_modules`, `.venv`, `dist`, `build`, `__pycache__`, binaries, large media, vendor dirs, dependency lockfiles unless relevant.
- Ask only about genuinely ambiguous sensitive folders.
- Prioritize rejected outputs and feedback over raw volume.

Then, for each approved source, record:

```
source: <path>
type: <session transcript / export / notes / workspace / posts / drafts / rejected / feedback>
era: <roughly when>
likely yields: <voice / taste / judgment / behavior / context / lexicon / anti-slop>
```

## Rules

- Discover widely; read only the approved scope. Never read beyond it. Never scan everything automatically without approval.
- If you hit secrets, tokens, client data, or private DMs: skip them, flag to the user, do not copy into any output.
- Rank sources by contrast value: rejected outputs and feedback first, then the user's own writing and session behavior, then references, then generic notes.
- Past agent sessions are the richest behavior source — they show how the user actually talks, corrects, and decides, not just what they say about themselves.
- If discovery and the user together yield zero rejected outputs or feedback, ask for two or three examples of AI output they disliked and one sentence each on why. That alone seeds judgment.md and anti-slop.md.

## Output of this step

A short audit summary: the discovered + approved scope, what each source will likely yield, what's missing, and the confirmed scan list. **Get approval before deep reading.**
