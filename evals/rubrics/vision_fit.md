# rubric — vision fit (manual)

Scores how well the repo matches the full vision: paste it into your agent → the agent discovers and scans your past AI sessions and workspaces across the system (with your approval) → builds your Creative Brain → writes a skill that compounds from how you talk, behave, and correct it, session to session.

Score each 1–5. 1 = absent. 3 = present but weak. 5 = real, specific, enforced by an eval.

| # | dimension | score (1–5) | notes |
|---|---|---|---|
| 1 | cross-system discovery — agent knows where AI sessions live, user doesn't hunt for paths | | |
| 2 | auto-discover vs manual-point — discovery leads, manual is the fallback | | |
| 3 | source breadth — Claude Code, ChatGPT/Claude exports, Cursor, Codex, notes, workspaces, projects | | |
| 4 | extraction depth — pulls "as much as it can", not a thin interview | | |
| 5 | workspace/project ingestion — treats project folders as first-class source, not just chat | | |
| 6 | behavior extraction — captures how the user works/talks/corrects across sessions, not just stated prefs | | |
| 7 | self-improving skill — compounds session to session, not a static profile | | |
| 8 | feedback compounding loop — corrections become durable rules that change future output | | |
| 9 | paste-and-go — minimal manual file-gathering; the agent does the finding | | |
| 10 | honest privacy — real auto-discovery WITHOUT overclaim; user approves scope, nothing leaves the machine | | |

## scoring bands
- 45–50: the repo delivers the vision
- 38–44: usable; close the weak dimensions
- 30–37: partial — discovery or behavior likely still manual
- <30: it's a manual file-pointing tool, not the vision

## the one hard line
Auto-discovery and honesty are NOT in tension here. A 5 on #1 AND #10 means: the agent actively finds sessions across the system (real), shows the user the full list, and reads only the approved scope (honest). If you scored #1 high by claiming silent total access, #10 must drop — that's overclaim, and the slop/privacy evals will catch it.
