# rejected-examples.md — template

## purpose

The gold file. Actual outputs the user killed, stored verbatim, with the real reason they died. Positive guidance tells an agent what to aim for; this file tells it what failure looks like in this user's world — which is the faster way to learn taste. This file is allowed to contain slop: that's what it's for.

Annotated rejected examples with reasons outrank generic banned-word lists. A ban on "unlock" is genre hygiene anyone could write; a killed draft with the user's raw reaction, what a better version would have kept, and the rule it teaches is identity. When in doubt about where to invest extraction effort, it's here, not in growing the word table in anti-slop.md.

## what belongs here

- the rejected output itself, verbatim (or the failing excerpt)
- where it came from (which agent/tool/draft, what task)
- the user's raw reaction, quoted ("sounds like LinkedIn", "this is cringe")
- the distilled failure reason — what *specifically* killed it
- what the fixed/accepted version did differently, if one exists

## what does not belong here

- generalized bans (anti-slop.md — link there when an example spawns a ban)
- outputs rejected for factual errors only (those are bugs, not taste)
- paraphrased versions of rejections — verbatim or nothing

## suggested sections

```md
## entries (newest first)
### #N — <date> — <one-line label>
task:
rejected output:
user reaction (raw):
why it died:
what worked instead:
```

## example entries

```md
### #1 — 2026-06-01 — launch post, corporate voice
task: write the launch post
rejected output: "We're thrilled to announce a revolutionary new way to supercharge your workflow…"
user reaction (raw): "absolutely not. sounds like every saas launch ever."
why it died: enthusiasm-performance + claim-stacking; zero specifics; could be anyone's product
what worked instead: opened with the actual problem in plain words, one concrete number
```

## update rule

Append every rejection worth remembering — newest first, numbered, dated. Never trim old entries; patterns emerge across them. When the same failure appears twice, spawn or strengthen a ban in anti-slop.md and link the entries.
