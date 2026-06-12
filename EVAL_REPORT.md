# EVAL_REPORT

date: 2026-06-12
command: `py evals/run_all.py` (Windows launcher; `python evals/run_all.py` on systems with python on PATH)
environment: Windows 11, Python via `py` launcher, no external dependencies

## results (final run)

| eval | result | what it checks |
|---|---|---|
| repo_structure_check | PASS | every required file exists; outputs/ contains only .gitkeep; prompts and templates are non-hollow (≥200 bytes each) |
| content_slop_check | PASS | banned/weak phrases and overclaims absent from README, AGENTS.md, REPO-USE-PROMPT.md, prompts/, templates/, docs/ (anti-slop.md and rejected-examples.md files exempt by design — listing banned phrases is their job) |
| protocol_completeness_check | PASS | AGENTS.md contains all 14 required protocol sections (role, do-not-write-content-first, source audit, interview, extraction, evidence/quotes, creative brain, output path, never-overwrite-templates, skill writing, before/after proof, feedback memory, privacy, quality checklist) |
| privacy_check | PASS | local-first / user-controls-files / no-cloud-upload / outputs-gitignored / secrets-client-data-DM warnings present across docs/privacy.md, README, AGENTS.md; .gitignore carries `outputs/**` + `!outputs/.gitkeep`; no scraping overclaims anywhere |
| example_proof_check | PASS | examples/pratham-mini/before-after.md has all six sections (task, generic output, creative brain output, what changed, user feedback, feedback memory update) and the two outputs are non-identical |
| agent_runnability_static_check | PASS | entry files (README, AGENTS.md, REPO-USE-PROMPT.md, prompts/00) establish: first action, ask-for-sources, output path, small interview rounds, template protection, skill generation, before/after proof, feedback updates |

Final run exit code: 0 — `RESULT: ALL PASS`.

## the loop, as it actually ran

**Iteration 1** — built all content files (root, prompts, templates, example, docs) and the six eval scripts, then ran `py evals/run_all.py`:

```
FAIL repo_structure_check
  - missing required file: EVAL_REPORT.md
PASS content_slop_check
PASS protocol_completeness_check
PASS privacy_check
PASS example_proof_check
PASS agent_runnability_static_check
RESULT: FAIL
```

One real failure: this report didn't exist yet (it's written from real results, so it can only exist after a run). No content or protocol failures surfaced — banned-phrase discipline was enforced during writing because the eval contract was designed before the prose.

**Harness verification** — before trusting the green slop check, it was negative-tested: a temp root was planted with one banned phrase ("supercharge") and one overclaim ("no setup needed") in a README, plus an exempt `anti-slop.md` containing banned terms. The eval caught exactly the two planted violations and skipped the exempt file. Output: `slop check negative-test: OK`.

**Iteration 2** — wrote this EVAL_REPORT.md, reran. All six pass (table above; raw output reproduced at the bottom of this file).

## fixes made during the loop

- added EVAL_REPORT.md (the only red→green transition; everything else passed on first run)

## manual rubric notes (self-review — independent review still pending)

- `evals/rubrics/agent_runnability.md`: not yet run with a live fresh agent. Static checks pass, but the rubric requires an actual session; scoring left blank by design — do not fill it without running the test.
- `evals/rubrics/taste_quality.md`: self-assessment — rejected-examples are structurally central (referenced by judgment, anti-slop, both review workflows, and the skill); before/after difference is legible in under 30 seconds; README leads with brains/context, not "AI writing tool". Honest caveat: self-scoring taste is exactly the bias this repo warns about; needs an outside reader (planned: Connor).

## remaining risks

1. **Static ≠ live.** agent_runnability is checked by phrase presence, not by an actual fresh-agent run. A live run (rubric #1) is the real test and hasn't happened yet.
2. **Marker-based evals can be gamed.** protocol/privacy/runnability checks match marker phrases; a future edit could keep markers while gutting meaning. The rubrics exist to catch this; run them after substantive changes.
3. **Single worked example.** pratham-mini proves the shape with one user type. v0.1's job is breadth.
4. **Self-scored taste.** See above — outside review pending.

## final status

All 6 script evals PASS (exit code 0). Manual rubrics documented, live-agent run pending. Repo committed only after the green run.

## raw output (final run)

```
PASS repo_structure_check
PASS content_slop_check
PASS protocol_completeness_check
PASS privacy_check
PASS example_proof_check
PASS agent_runnability_static_check

RESULT: ALL PASS
```
