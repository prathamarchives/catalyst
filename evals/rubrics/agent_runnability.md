# rubric — agent runnability (manual)

Run this with a **fresh agent** (a new session with no prior context) pointed at the repo via REPO-USE-PROMPT.md. Score each question 1–5 (1 = total failure, 3 = works with friction, 5 = flawless). Record what actually happened, not what should have.

| # | question | score (1–5) | notes |
|---|---|---|---|
| 1 | Can the agent start without extra explanation beyond the use-prompt? | | |
| 2 | Does it ask the right first question (where the source material lives)? | | |
| 3 | Does it avoid generating final creative work too early? | | |
| 4 | Does it interview in small rounds instead of question walls? | | |
| 5 | Does it create outputs in the right folder (`outputs/<name>/`), leaving templates untouched? | | |
| 6 | Does it use evidence — quoting the user's actual material for voice/taste claims? | | |
| 7 | Does it separate observed patterns from assumptions and get assumptions confirmed? | | |
| 8 | Does it run a real before/after proof with a specific "what changed"? | | |
| 9 | Does it update feedback memory after corrections (raw quote + rule + patched files)? | | |
| 10 | Does it write a useful, user-specific skill (not a template copy)? | | |

## scoring

- 45–50: ship-quality runnability
- 35–44: usable; fix the lowest-scoring items before promoting the repo
- below 35: the protocol has a hole — find which entry file failed to carry the instruction and patch it

## notes for the tester

- test with the weakest agent you realistically expect users to bring, not just the strongest
- every score below 4 should produce a patch to README/AGENTS/prompts — the rubric exists to generate fixes, not grades
- log the session transcript path here for future comparison: ______
