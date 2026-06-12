# workflow — distill memory (pratham)

Run periodically so feedback-memory.md stays sharp as it grows. Full protocol: [prompts/09-distill-and-decay-memory.md](../../../prompts/09-distill-and-decay-memory.md).

## when

- every 10 raw feedback entries, or weekly/monthly
- forced when feedback-memory.md takes more than a couple of minutes to read
- after the blind A/B win-rate stalls

## steps

1. Read feedback-memory.md, context.md, rejected-examples.md end to end.
2. Merge duplicate rules into one with all its dated receipts; keep raw quotes verbatim.
3. Promote corrections given 2+ times into active rules + anti-slop.md/judgment.md.
4. Decay stale context into retired/stale with the reason; taste and judgment never decay by age.
5. Surface contradictions to Pratham; he rules; record it in the distillation log.
6. Never delete a strong rejected example without a better replacement.
7. Log the pass in feedback-memory.md's distillation log.

## rules

- compress rules, never quotes
- retire with a reason; don't delete
- current context and durable taste age in opposite directions — keep them separate
