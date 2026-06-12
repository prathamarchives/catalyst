# blind A/B eval

The before/after proof has a weakness: the person judging it knows which output used the Creative Brain. Knowing the labels biases the judgment — you root for the brain because you built it. The blind A/B eval removes that bias.

## purpose

Measure whether outputs produced with the Creative Brain loaded are actually preferred when the labels are hidden. Not "does it look different" — "does the user pick it when they can't tell which is which."

## protocol

1. **Choose one real task.** A post, a reply, a blurb — something the user actually needs, same standard as the before/after proof.
2. **Generate output A without the Creative Brain.** Cold, no brain files, no user quotes. The baseline must be competent — clear, accurate, the genuinely best generic version. Do not strawman the baseline; a win over deliberately bad output proves nothing.
3. **Generate output B with the Creative Brain loaded** (full mode, per the generated skill).
4. **Hide and shuffle the labels.** Present the two outputs as "option 1" and "option 2" in random order. Do not reveal which is which. Keep the mapping somewhere the user can't see until after they choose.
5. **The user chooses a winner blind.**
6. **The user explains why** — in their own words, verbatim into the log.
7. **Log the result** in the blind A/B log (template: `templates/evals/blind-ab-log.md`).
8. **Reveal the labels, then update feedback-memory.md.** Never patch memory before the reveal — the choice must stay uncontaminated.
9. **Track win-rate over time.**

## the metric

```
brain_win_rate = brain_wins / total_blind_tests
```

Each log entry also tracks:

- task type (post / reply / blurb / outline / other)
- date
- winner (brain / generic / tie)
- the user's verbatim reason
- what changed in memory after the reveal
- effectiveness after publishing, if applicable (see below)

A healthy Creative Brain trends upward: as feedback-memory grows and distillation runs, brain_win_rate should climb. A flat or falling rate is signal — the brain is thin, stale, or contradicting itself. Run the memory distillation workflow and collect more contrast material.

## blind preference is not the only metric

Preference measures taste-match. It does not measure whether the output worked. Track effectiveness too, where it applies:

- did the post land — replies, saves, the audience it was meant for?
- did the DM get a response?
- did the artifact get real feedback from a real person?
- did the output help the user act — ship, send, decide?

An output the user prefers but never publishes is a weaker win than one that went out and did its job. Log both. When preference and effectiveness disagree (the user picked A, but B performed), that disagreement is high-value material for judgment.md.

## cadence

Run a blind test whenever a real task allows it — no special setup needed beyond hiding labels. Aim for enough entries that the win-rate means something (5+ before reading trends). One rigged demo is worth less than three honest losses with reasons.

## honest losses

When the generic output wins, that is not a failure of the eval — it is the eval working. Log it, get the reason, and feed it back: what did the brain version get wrong? Too much voice where the task needed plain function? A stale rule? The losses are where the brain learns; see [memory-lifecycle.md](memory-lifecycle.md).
