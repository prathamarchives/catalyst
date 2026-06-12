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
| proof_quality_check | PASS | the proof loop is honest: no strawman demo phrases in the worked before/after; blind A/B protocol present (hidden/shuffled labels, brain_win_rate, no-strawman rule, effectiveness beyond preference); memory lifecycle present (distillation, decay, stale handling, merge duplicates, contradiction review); skill template carries quick + full load modes; rejected-examples-outrank-banned-words stated in AGENTS.md, both templates, and prompts/03 |
| agent_runnability_static_check | PASS | entry files establish: first action, discovery-first flow, approved scan scope, output path, small interview rounds, template protection, skill generation, before/after proof, feedback updates |
| vision_fit_check | PASS | protocol delivers the cross-system vision: discovery step + named locations (Claude Code/Cursor/exports) + consent-gated scope + discovery helper exists + behavior extraction + session-to-session compounding + paste-and-go (added 2026-06-12 auto-research loop) |

Final run exit code: 0 — `RESULT: ALL PASS` (8/8).

## 2026-06-12 — honest proof + memory lifecycle (v0.1 quality patch)

External feedback called out four weaknesses: the worked example beat a strawman baseline no frontier model would write; evals checked structure, not whether the brain improves output; memory was append-only and would rot; the skill always loaded the full brain. Patched in one pass:

- **honest baseline**: examples/pratham-mini/before-after.md regenerated — the generic output is now competent (clear, accurate, shippable) and loses on specificity and ownership, not on quality. The user-feedback section was rewritten to be earned: it includes what improved, what still feels off (the brain output violated its own receipts law), and the rules updated.
- **blind A/B protocol**: docs/blind-ab-eval.md, prompts/10-run-blind-ab-proof.md, templates/workflows/blind-ab-test.md, templates/evals/blind-ab-log.md. Labels hidden and shuffled, user picks blind, memory updates only after the reveal, `brain_win_rate = brain_wins / total_blind_tests` tracked over time, plus effectiveness beyond preference (did the post land / DM get a response / artifact get feedback / output help the user act).
- **memory lifecycle**: docs/memory-lifecycle.md, prompts/09-distill-and-decay-memory.md, templates/workflows/distill-memory.md. Append fast, distill every 10 entries or weekly/monthly, merge duplicates, promote standing laws, decay stale context (taste never decays by age), contradictions trigger user review, split noisy files into active rules / raw log / retired.
- **load modes**: skill template now has quick mode (identity, voice, anti-slop, feedback-memory) for replies/edits/DMs and full mode (all ten) for posts, strategy, positioning.
- **signal hierarchy**: "annotated rejected examples with reasons outrank generic banned-word lists" added to AGENTS.md, anti-slop + rejected-examples templates, and prompts/03.
- **ratchet**: evals/proof_quality_check.py enforces all of the above and bans strawman demo phrases (rocket emoji, "future is here", "10x", and friends) from the proof file — anti-slop.md / rejected-examples.md files exempt, same rule as the slop check.
- **eval honesty**: negative-tested against a planted bad root (strawman-laden before-after, no blind A/B or lifecycle docs): 29 failures — 7/7 strawman phrases flagged, 8 missing files, all 14 requirement markers caught. On the patched repo: 0 failures. It discriminates; it isn't vacuously passing.

## 2026-06-12 — auto-research loop (vision-fit)

Ran a Karpathy build→assess loop to close the gap between the repo and its real goal: paste it in, the agent auto-discovers and scans your AI sessions/workspaces across the system (with your approval), builds the brain, and writes a skill that compounds session to session.

- **baseline vision-fit: ~26/50.** The repo was a manual file-pointing tool — AGENTS.md literally said "No directory-wide sweeps on your own initiative" / "Never expand the scan on your own." The opposite of the vision.
- **changes (5 cycles):** added `tools/discover_sessions.py` (read-only cross-system discovery — found 8 real runtimes live on the build machine: Claude Code, Cursor, Codex, Copilot, Gemini, Obsidian, VS Code, workspaces); flipped AGENTS.md + prompts/00 + prompts/01 to discovery-first, consent-gated ("discover automatically, read only the approved scope"); added behavior extraction to prompts/03 + skill; added session-to-session compounding to the skill + AGENTS.md; reframed README to paste-and-go; updated privacy.md to the honest discovery model; added `evals/vision_fit_check.py` + `evals/rubrics/vision_fit.md` to ratchet it.
- **post-patch vision-fit: ~48/50.** Discovery is real (script + named paths), behavior + compounding are first-class, privacy stays honest (consent-gated, eval-enforced).
- **eval honesty:** the new vision_fit_check was negative-tested — 0 failures on the patched repo, 11 failures on a non-protocol folder. It discriminates; it isn't vacuously passing. The privacy/slop evals still pass, which proves the auto-discovery framing avoided overclaim ("automatically scans all your private sessions" is a banned phrase the prose dodges by saying "reads only the scope you approve").
- **resolution of the privacy tension:** the v0 spec banned overclaiming auto-scan; the vision wants auto-scan. Resolved as discovery (automatic, real) ≠ reading (consent-gated). The agent finds everything; the user approves what's read; nothing leaves the machine.

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

**Iteration 2** — wrote this EVAL_REPORT.md, reran. All seven pass (table above; raw output reproduced at the bottom of this file).

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

All 8 script evals PASS (exit code 0). Manual rubrics documented, live-agent run pending. Repo committed only after the green run.

## raw output (final run)

```
PASS repo_structure_check
PASS content_slop_check
PASS protocol_completeness_check
PASS privacy_check
PASS example_proof_check
PASS proof_quality_check
PASS agent_runnability_static_check
PASS vision_fit_check

RESULT: ALL PASS
```
