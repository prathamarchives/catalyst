# workflow — distill memory

Run periodically to keep memory from rotting. Append-only memory degrades: duplicates pile up, context goes stale, contradictions accumulate. Full protocol: [prompts/09-distill-and-decay-memory.md](../../prompts/09-distill-and-decay-memory.md); model: [docs/memory-lifecycle.md](../../docs/memory-lifecycle.md).

## when

- every 10 feedback entries, or weekly/monthly — whichever fits usage
- forced: feedback-memory.md takes more than a couple of minutes to read
- after blind A/B win-rate stalls

## steps

1. **Read feedback-memory.md, context.md, rejected-examples.md** end to end.
2. **Merge duplicate rules** — one rule, all its dated receipts; raw quotes preserved verbatim.
3. **Promote recurring corrections** (2+) to standing laws: top of file, mirrored to anti-slop.md / judgment.md, into the skill's red flags.
4. **Decay stale context** — expired context entries move to a retired/stale section with the reason; time-sensitive rules carry date + context tags. Taste and judgment never decay by age.
5. **Surface contradictions to the user** — both rules, dates, quotes; the user rules; record the ruling. Never resolve silently.
6. **Audit rejected-examples.md** — never delete a strong example without a better replacement.
7. **Split if noisy:** active rules / raw feedback log / retired-stale rules; update the skill's load order.
8. **Log the pass** — date, merges, promotions, retirements, rulings.

## rules

- compress rules, never quotes — verbatim user language survives every pass
- nothing is destroyed; retirement with a reason beats deletion
- current context and durable taste live separately — they age in opposite directions
