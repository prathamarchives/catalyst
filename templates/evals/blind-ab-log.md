# blind A/B log — template

Copy into `outputs/<name>/evals/blind-ab-log.md` on the first blind test. One table row per test, plus a running win-rate. Protocol: [docs/blind-ab-eval.md](../../docs/blind-ab-eval.md), [prompts/10-run-blind-ab-proof.md](../../prompts/10-run-blind-ab-proof.md).

## running metric

```
brain_win_rate = brain_wins / total_blind_tests
```

| total blind tests | brain wins | generic wins | ties | brain_win_rate |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | — |

## entries (newest first)

```md
### #N — <date> — <task type: post / reply / blurb / outline / other>
task: <one line>
winner: <brain / generic / tie>
user reason (verbatim, captured blind): "<their words>"
memory update (after reveal): <rule extracted + files patched, or "none">
effectiveness (if published): <did it land — replies / response / feedback / helped user act — or "not published" / "pending">
```

## example entry

```md
### #1 — 2026-06-20 — post
task: short X post on why agents need taste files
winner: brain
user reason (verbatim, captured blind): "option 2 sounds like a person, option 1 explains itself too much"
memory update (after reveal): rule — never open by defining the concept; patched voice.md
effectiveness (if published): posted; 3 quote-replies from target audience, one DM
```

## notes

- log losses and ties as faithfully as wins — losses are where the brain learns
- update the running metric table on every entry
- 5+ entries before reading trends into the rate
