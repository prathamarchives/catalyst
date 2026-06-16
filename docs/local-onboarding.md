# local onboarding

Guided onboarding gets a usable Catalyst Brain on disk fast, without making the user hunt for paths and without reading anything they didn't approve. It runs two ways: as an agent following `AGENTS.md`, or through the optional control panel (`apps/control-panel/`). Both produce the same local files under `outputs/<name>/`.

## Principle

Ask little, build locally, prove on real work. The brain is seeded from the user's typed answers first; deeper material comes only from sources the user approves.

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

1. **Welcome** — explain local-first in plain language: files on your machine, nothing uploaded by default, you control any scan.
2. **Collect answers** — the 5–7 above.
3. **Read-only discovery** — run `tools/discover_sessions.py` (or the panel's Sources tab). This checks where AI sessions, notes, exports, and workspaces live. It reads no file contents — path metadata only.
4. **Recommend safe scope** — show discovered *categories*, not giant path dumps. Recommend the safe preset (AI sessions, notes, markdown workspaces; exclude secrets/tokens/private DMs/client data/vendor/build/binaries).
5. **Approval gate** — if the starting prompt already authorized a recommended safe scan, proceed (autonomous authorized mode). Otherwise ask exactly one compact approval question: *approve recommended scan, edit scope, or manual mode?*
6. **Scan approved scope only** — read contents only inside what was approved. Exclusions always bind.
7. **Generate the brain** — create `outputs/<name>/catalyst-brain/` plus `skills/`, `workflows/`, `evals/` from `templates/`. Seed `identity/goals/constraints/taste/rejected-examples/task-patterns` with the answers as observed evidence.
8. **Run the first proof task** — take it through the task-time evaluation loop (`prompts/06-task-time-evaluation.md`): load relevant files, produce, review against standards, show the user.
9. **Capture feedback and update** — route the reaction into `feedback-memory.md` and patch the right brain/skill/eval (`prompts/07-update-from-feedback.md`).

## In the control panel

The Onboarding screen collects the 5–7 answers, lets the user pick recommended / manual / skip scan, and shows the default exclusions before anything is read. Submitting builds the seeded brain locally (no scan on that screen). The Sources screen runs read-only discovery and holds the one approval question. The Proof screen runs the first task-time review. See [docs/control-panel.md](control-panel.md).

## Privacy

Discovery is read-only. Content scanning is authorized. Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, dependency folders, and sensitive material. Outputs are gitignored. A hosted model/provider may receive approved context — only matters if you enable BYOK or run inside a hosted agent. See [docs/privacy.md](privacy.md) and [docs/permission-model.md](permission-model.md).
