# 09 — distill and decay memory

Goal: keep the Creative Brain's memory sharp as it grows. Append-only memory degrades — duplicates accumulate, context goes stale, rules start contradicting each other. This step is the maintenance pass that keeps compounding honest. Full model: [docs/memory-lifecycle.md](../docs/memory-lifecycle.md).

## When to run

- every 10 feedback entries, or on a weekly/monthly rhythm — whichever fits usage
- forced: when feedback-memory.md takes more than a couple of minutes to read
- after a stretch of blind A/B losses (the win-rate stalling is a rot signal)

## Procedure

1. **Read all of feedback-memory.md**, plus context.md and rejected-examples.md. You are auditing memory, not writing content.

2. **Merge duplicate rules.** Entries teaching the same lesson collapse into one rule carrying all its dated receipts. Preserve every raw quote — compress the rules, never the user's language.

3. **Promote recurring corrections to standing laws.** Any correction given twice or more becomes a standing law: top of feedback-memory.md, mirrored into anti-slop.md or judgment.md, and into the skill's red flags.

4. **Decay stale context.** For each context-dependent entry, ask: is this still true? Time-sensitive rules should carry their date and context ("while the account is small", "during the launch"). Move expired entries to a retired/stale section with the reason they retired. Do not decay taste or judgment rules by age — context goes stale; taste gets proven.

5. **Surface contradictions for user review.** Where two rules conflict, present both with dates and quotes. Ask the user which wins. Record the ruling and retire the loser. Never resolve a contradiction silently.

6. **Check rejected-examples.md.** Never delete a strong rejected example without a replacement that teaches the same failure better. Trim only true redundancy.

7. **Split the file if it's noisy.** When feedback-memory.md is too long to load comfortably: `active rules` (standing laws + live rules, loaded every time), `raw feedback log` (full dated history, on demand), `retired/stale rules` (with retirement reasons). Update the generated skill's load order to match.

8. **Log the pass.** Date, what was merged, what was promoted, what was retired, what the user ruled on. The distillation history is itself memory.

## Rules

- distillation compresses rules, never quotes — verbatim user language is evidence and survives every pass
- nothing is destroyed; retired rules move to a retired section with reasons, because why a rule died is taste data
- keep current context separate from durable taste/judgment — they age in opposite directions
- if the user is unavailable for contradiction review, flag and leave both rules; do not guess
