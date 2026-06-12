# workflow — review an output

Use to review any creative output (yours or another agent's) against the user's brain before it ships. This is the brain acting as an eval.

## steps

1. **Load** judgment.md, anti-slop.md, rejected-examples.md, feedback-memory.md (standing laws first).
2. **Ban scan** — any anti-slop words, structures, or vibes present? Each hit is an automatic fix-before-ship.
3. **Corpse match** — does any part resemble an entry in rejected-examples.md? Name the entry if so.
4. **Standing laws check** — does it violate any law in feedback-memory.md?
5. **Judgment pass** — run the user's kill rules and pre-final checklist from judgment.md.
6. **Ownership test** — could this appear under anyone's name unchanged? If yes: it's generic; identify which brain file's input is missing from it.
7. **Verdict** — one of: `ship` / `fix: <named issues>` / `kill: <which rule it died on>`.

## report format

```
verdict: fix
- anti-slop hit: "thrilled to announce" (banned vibe: enthusiasm performance)
- resembles rejected-examples #1 (corporate launch voice)
- ownership test: fails — no user phrases, no receipts
```

## rules

- name the rule behind every flag — "feels off" is not a review
- a clean review names what the output got *right* against the brain too (one line); that confirms the brain is being used, not bypassed
- if the output is fine but the brain was silent somewhere it shouldn't be, log the gap
