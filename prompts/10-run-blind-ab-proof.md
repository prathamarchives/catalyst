# 10 — run the blind A/B proof

Goal: measure whether the Creative Brain actually wins when the user can't see the labels. The before/after proof (prompt 06) shows the difference; this proof tests the preference without bias. Full protocol and metric: [docs/blind-ab-eval.md](../docs/blind-ab-eval.md).

## Procedure

1. **Choose one real task with the user.** Same standard as prompt 06: something they actually need.

2. **Generate output A — no Creative Brain.** Cold. And honestly: the baseline must be competent — clear, accurate, the best generic version you can produce. **Do not strawman the baseline.** A brain that only beats deliberately bad output has proven nothing. No fake hype, no cartoon slop — frontier models don't write that way, and the test is against reality.

3. **Generate output B — full Creative Brain loaded**, per the generated skill's full mode. Check rejected-examples.md before finalizing.

4. **Hide and shuffle the labels.** Show the user "option 1" and "option 2" in random order. Keep the label mapping hidden — written somewhere the user won't see until after the choice.

5. **User picks a winner, blind.** Then asks nothing else first: get their reason in their own words, verbatim.

6. **Reveal the labels.**

7. **Log the result** in the blind A/B log (copy `templates/evals/blind-ab-log.md` into `outputs/<name>/evals/` on first run): task type, date, winner, verbatim reason, memory update, and — when the output ships — effectiveness (did the post land, did the DM get a response, did the artifact get feedback, did it help the user act).

8. **Update feedback-memory.md only after the reveal.** The reason behind the pick is feedback like any other — run prompt 07 on it. Updating before the reveal contaminates the test.

9. **Update the running win-rate:**

```
brain_win_rate = brain_wins / total_blind_tests
```

## Reading the results

- track the rate over time; the compounding claim predicts it climbs as memory grows and distillation runs
- a generic win is the eval working, not failing — log it, extract why, feed it back
- preference is not the only metric: an output the user picked but never published is a weaker win than one that shipped and worked
- 5+ entries before trusting any trend; one test is an anecdote

## Rules

- never reveal labels before the choice, never patch memory before the reveal
- never sandbag output A or pick tasks the brain is guaranteed to win
- ties are legal and logged as ties
