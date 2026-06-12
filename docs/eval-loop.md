# the eval loop

This repo was built with the loop it preaches. This doc explains how to run it — for contributors, and for anyone extending the protocol.

## the loop

```
1. build      — write/modify repo files
2. run evals  — python evals/run_all.py   (Windows fallback: py evals/run_all.py)
3. read       — every FAIL prints exactly what's missing/violated and where
4. patch      — fix only what failed; don't refactor green areas mid-loop
5. rerun      — back to step 2
6. commit     — only when all evals pass
```

`run_all.py` exits 0 when everything passes, 1 otherwise — wire it into CI or a pre-commit hook if you want the gate enforced mechanically.

## what the evals check

| eval | guards |
|---|---|
| repo_structure_check | every required file exists; outputs/ stays empty except .gitkeep; no hollow templates |
| content_slop_check | banned phrases and overclaims stay out of the repo's own prose |
| protocol_completeness_check | AGENTS.md keeps every required protocol section as the repo evolves |
| privacy_check | privacy commitments stay present and uncontradicted |
| example_proof_check | the worked example keeps a real, complete before/after proof |
| agent_runnability_static_check | a fresh agent can still find its first action, the output path, and the full loop |

Two manual rubrics (`evals/rubrics/`) cover what scripts can't: live agent-runnability and taste quality. Score them by hand after substantive changes.

## design rules for these evals

- standard library only, no external dependencies
- deterministic: same files in, same verdict out — no LLM calls, no network
- loud failures: every FAIL names the file and the missing/violating item
- exemptions are explicit: `anti-slop.md` and `rejected-examples.md` files are skipped by the slop check because listing banned phrases is their job — eval design must never make anti-slop documentation impossible

## why this matters

A one-shot generation looks done; it isn't verified. The loop converts "looks done" into "checked against an explicit standard, failed, fixed, and re-checked." That's the same argument the Creative Brain makes for creative work: coding loops need tests, creative loops need taste — and both need the standard written down where a machine or an agent can check it.

Prompting alone produces plausible output. Loops + evals produce reliable output. Memory (in this repo: EVAL_REPORT.md, the fix log, and the brain's feedback-memory pattern) makes the next loop start smarter than the last.
