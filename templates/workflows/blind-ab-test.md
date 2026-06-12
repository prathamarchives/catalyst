# workflow — blind A/B test

Run when a real task can double as a measurement. This is the unbiased check on the whole system — see [prompts/10-run-blind-ab-proof.md](../../prompts/10-run-blind-ab-proof.md) for the full protocol and [docs/blind-ab-eval.md](../../docs/blind-ab-eval.md) for the reasoning.

## steps

1. **Pick one real task** the user actually needs.
2. **Output A: no brain.** Cold and competent — the best generic version. Do not strawman the baseline.
3. **Output B: full brain loaded** per the skill's full mode.
4. **Hide and shuffle labels.** Present as option 1 / option 2, random order, mapping hidden.
5. **User picks blind**, then gives the reason in their own words — capture verbatim.
6. **Reveal labels.**
7. **Log it** in `outputs/<name>/evals/blind-ab-log.md`: task type, date, winner, verbatim reason, memory update, effectiveness if published.
8. **Update feedback-memory.md** — only after the reveal — via the update-from-feedback workflow.
9. **Update the win-rate:** `brain_win_rate = brain_wins / total_blind_tests`.

## rules

- labels stay hidden until after the choice; memory updates wait until after the reveal
- ties are logged as ties; generic wins are logged with extra care — they teach the most
- track effectiveness beyond preference: did the post land, did the DM get a response, did the artifact get feedback, did it help the user act
- a stalling win-rate while memory grows = run the distill-memory workflow
