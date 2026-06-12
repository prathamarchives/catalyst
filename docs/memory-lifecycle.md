# memory lifecycle

Append-only memory degrades over months. Corrections pile up, duplicates accumulate, rules contradict each other, and context that was true in January is quietly wrong by June. A feedback-memory.md that nobody prunes becomes noise the agent skims instead of law the agent follows. This doc defines how memory stays sharp: append fast, distill periodically, decay what's stale.

## the lifecycle

```
correction → append (immediately, raw)
          → distill (periodically: merge, promote, decay)
          → review (user resolves contradictions)
```

## rules

- **Append corrections immediately.** Raw quote, date, distilled rule, files patched — same as always. Speed of capture beats tidiness of capture.
- **Periodically distill.** Run the distillation pass (workflow: `templates/workflows/distill-memory.md`, protocol: `prompts/09-distill-and-decay-memory.md`).
- **Merge duplicate rules.** Five entries that all say "no dramatic buildup" become one rule with five dated receipts.
- **Promote recurring corrections to standing laws.** Twice is the threshold; a standing law sits at the top of the file and in the skill's red flags.
- **Decay stale context.** Context entries (live projects, current goals, current offers) expire. If an entry hasn't been true or referenced in months, move it to a retired section — don't let dead context steer live output.
- **Mark time-sensitive rules with date and context.** "no threads right now (2026-06, while account is small)" is a rule with a shelf life; tag it so future distillation knows it can lapse.
- **Preserve raw quotes.** Distillation compresses rules, never the user's verbatim language. The quotes are evidence; the rules are derived. Keep both.
- **Never delete a strong rejected example without a replacement.** rejected-examples.md only shrinks when a newer example teaches the same lesson better.
- **Contradictions trigger user review.** When two rules conflict, do not silently pick one. Surface both with their dates and quotes, ask the user which wins, and record the ruling. Newer-beats-older is the default only until the user rules.
- **Keep current context separate from durable taste and judgment.** context.md decays; voice/taste/judgment compound. Distillation must never "expire" a taste rule just because it's old — age makes context stale but makes taste proven.

## cadence

- **after every feedback event:** quick update — append the entry, patch the affected file. Minutes, not a ceremony.
- **every 10 feedback entries, or weekly/monthly** (whichever rhythm fits how often the brain is used): run the full distillation pass.
- **forced review when files get too long:** if feedback-memory.md takes more than a couple of minutes to read, distillation is overdue regardless of cadence.

## when feedback-memory.md gets noisy

Split it:

- **active rules** — the standing laws and live rules an agent must load every time; short, ruthless
- **raw feedback log** — the full dated append-only history with verbatim quotes; the evidence archive
- **retired / stale rules** — rules that expired, were superseded, or lost a contradiction review; kept with the reason they retired, because retired rules are themselves taste data

The skill loads active rules always, the raw log on demand. Nothing is destroyed; the load path just stops paying for history on every task.

## why this matters

The compounding claim — sharper every session — is only true if memory quality compounds, not just memory volume. Volume without distillation is the LinkedIn-feed version of memory: technically growing, practically useless. The blind A/B win-rate ([blind-ab-eval.md](blind-ab-eval.md)) is the external check: if the rate stalls while entries pile up, the memory is rotting, and distillation is the fix.
