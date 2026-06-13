# 08 — install and run

The operating procedure for when the user says **"install this repo"** (or "install this and build my Creative Brain"). This is the step the previous version got wrong: an agent cloned the repo, saw no package manifest, and stopped. Do not do that. This file is how you go from a bare repo link to a finished Creative Brain with almost no burden on the user.

## Hard rules (read these first)

- **Do not stop at clone.** Cloning is step one of install, not the whole thing.
- **Do not say "no package.json, done"** or **"nothing to install, done"** and stop. Absence of a manifest is expected; this is a protocol repo.
- **Do not ask the user to find their session paths.** You discover them. The user only approves scope (unless they pick manual mode).
- **Never scan everything automatically.** Discovery is automatic; reading is authorization-gated. Scan only the authorized scope — and only the *recommended safe scope* unless the user widened it.
- **Two modes.** If the user's prompt already authorized the recommended scan (**autonomous authorized mode**), proceed without a second approval question. If authorization is ambiguous (**cautious approval mode**), exactly one approval question gates reading. Never invent blanket permission the user didn't give.
- Minimize user burden. The user is needed for authorization and taste feedback — almost nothing else.

## 1. Classify the repo

Recognize this as an **agent protocol / repo-as-product**, not an application. Signal: lots of markdown (`AGENTS.md`, `prompts/`, `templates/`), a tiny stdlib eval harness, and a read-only discovery helper — and no app entrypoint. Do not look for a server to start or a UI to open. The product is the protocol.

## 2. Clone / open

If given a link, clone it (`git clone <repo-url>`). If it's already open in the workspace, use it in place. Confirm the files are present (`AGENTS.md`, `prompts/`, `templates/`, `evals/`, `tools/`).

## 3. Check package manifests — and expect none

Look for `package.json`, `requirements.txt`, `setup.py`, `pyproject.toml`. Finding none is the expected, correct state. There are **no dependencies**; the only code is stdlib-only.

## 4. Explain the protocol install

Tell the user, in substance:

> There is no package install. This is a protocol repo, so install is complete. Next I'll run setup: discover sources, recommend a scan scope, ask approval, build the brain, write the skill, and run proof.

This is the line that prevents the stop-at-clone failure. Say it, then keep going.

## 5. Verify safely (optional)

You may run the eval harness to confirm the repo is intact:

```
py evals/run_all.py        (Windows launcher)
python evals/run_all.py    (python on PATH)
```

Exit `0` / `RESULT: ALL PASS` = intact. This is **optional verification** — skipping it does not block setup.

## 6. Handle a permission block

A permission classifier may refuse to run code from a freshly cloned external repo. That is a reasonable guardrail. Do not treat it as install failure. Say so plainly, tell the user they can run `py evals/run_all.py` themselves if they want the check, and **continue to setup** — verification is optional and never gates the build.

## 7. Run discovery

Run `tools/discover_sessions.py` (or replicate its logic). It checks known locations across the system and prints the ones that exist — read-only, paths only, no contents. This is how you avoid making the user hunt for where Cursor/Claude/Codex store history.

## 8. Recommend a scan preset (don't dump paths)

Group the discovered locations and propose a **safe default**, not a list of 47 folders. The presets:

- **recommended scan:** AI sessions + exports + markdown-heavy workspaces. Exclude secrets, client data, private DMs, binaries, vendor/build dirs.
- **full scan:** all discovered locations, still excluding obvious vendor/build/binary junk.
- **manual:** the user names exact paths.

Triage rules for what's worth reading:

- Inventory before deep reading.
- Prefer `.md`, `.txt`, `.json`, `.jsonl`, `.csv`, chat exports, posts, drafts, feedback, rejected outputs.
- Skip by default: `.git`, `node_modules`, `.venv`, `dist`, `build`, `__pycache__`, binaries, large media, vendor dirs, dependency lockfiles unless relevant.
- Ask only about genuinely ambiguous sensitive folders.
- Prioritize rejected outputs and feedback over raw volume.

## 9. Authorize the scan (mode-dependent)

Pick the mode from the user's opening instruction:

- **Autonomous authorized mode (Mode A):** the prompt already authorized the recommended scan of AI sessions / workspaces / agent memory / markdown, excluding sensitive folders. **Do not ask again.** State the scope in one line and proceed:
  > Authorized — scanning AI sessions, exports, and markdown-heavy workspaces; excluding secrets/client/private-DM/vendor/build/binary folders.
- **Cautious approval mode (Mode B):** authorization is ambiguous. Ask exactly one question, in this shape:
  > I recommend scanning AI sessions, exports, and markdown-heavy workspaces while excluding secrets/client/private-DM/vendor/build/binary folders. Approve recommended scan, edit scope, or manual mode?

Not a quiz, not a path-by-path interrogation. One decision at most — and zero if the user already authorized it.

## 10. Scan only the approved scope

Read contents only inside what the user approved. Never expand beyond it. If you hit secrets/tokens/client data/private DMs, skip and flag — never copy them into outputs. Then audit per [01-source-audit.md](01-source-audit.md): inventory each source and what it likely yields.

## 11. Build the Creative Brain

Run the rest of the protocol in order:

- interview to fill gaps ([02](02-interview-user.md)) — small rounds only
- extract with evidence quotes, observed vs assumed ([03](03-extract-creative-identity.md))
- build all ten brain files, the skill, and copy all five workflows; initialize the blind A/B log ([04](04-build-creative-brain.md), [05](05-write-agent-skill.md))
- run the before/after proof ([06](06-run-before-after-proof.md)) and, when possible, the blind A/B proof ([10](10-run-blind-ab-proof.md))
- collect feedback and fold it into memory ([07](07-update-from-feedback.md)); set the distillation cadence ([09](09-distill-and-decay-memory.md))

## 12. Final handoff

End every run by telling the user exactly how to use what you built:

- where the brain lives (`outputs/<name>/`)
- how an agent loads it next time (load the skill; quick mode vs full mode)
- the blind A/B scoreboard and where it's logged
- the distillation cadence (every ~10 feedback entries or weekly/monthly)
- what's still thin and worth feeding the brain next (usually more rejected examples / feedback)

The user should finish knowing what they have and what to do next — not holding a pile of files they have to wire together themselves.
