# workflow — blind A/B test (pratham)

Run when a real task can double as a measurement. The unbiased check on the brain — full protocol in [prompts/10-run-blind-ab-proof.md](../../../prompts/10-run-blind-ab-proof.md).

## steps

1. Pick one real task Pratham needs (a post, a reply).
2. Output A: no brain. Cold and competent — the best generic version. Do not strawman the baseline.
3. Output B: full brain loaded.
4. Hide and shuffle labels — option 1 / option 2, mapping hidden.
5. He picks blind, gives the reason in his own words (capture verbatim).
6. Reveal labels.
7. Log it in `../evals/blind-ab-log.md`: task type, date, winner, verbatim reason, memory update, effectiveness if published.
8. Update feedback-memory.md (after the reveal) via update-from-feedback.
9. Update the win-rate: `brain_win_rate = brain_wins / total_blind_tests`.

## rules

- labels hidden until after the choice; memory updates wait until after the reveal
- a generic win is logged with care — it teaches the most
- track effectiveness beyond preference: did the post land, did the DM get a response
