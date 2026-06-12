# feedback-memory.md — template

## purpose

Every correction the user gives, distilled into durable rules. This file is what makes the system compound: without it, every session starts from zero and the user repeats themselves forever. With it, each correction is paid for once.

## what belongs here

- every meaningful correction: the raw quote, the distilled rule, the date
- which brain files were patched in response
- recurring-correction tracker (a correction given twice is a standing law)
- resolutions of conflicts ("rule A vs rule B — user said A wins for posts")

## what does not belong here

- the failed outputs themselves (rejected-examples.md)
- compliments without information ("nice" teaches nothing; "nice — because it leads with the number" does)
- the agent's interpretation *replacing* the raw quote — always keep both

## structure — four sections

Memory has a lifecycle, not just an append. Keep these four sections so the file stays sharp as it grows (full model: [docs/memory-lifecycle.md](../../docs/memory-lifecycle.md)):

```md
## active rules
The standing laws + live rules an agent must load every time. Short, ruthless.
Corrections given 2+ times live here. This is what quick mode loads.

## raw feedback log (newest first)
The full dated append-only history with verbatim quotes — the evidence archive.
### <date>
raw: "<verbatim user words>"
rule: <the generalized preference>
patched: <which files were updated>

## retired / stale rules
Rules that expired, were superseded, or lost a contradiction review — kept with
the reason they retired, because why a rule died is itself taste data.

## distillation log
Dated record of each distillation pass: what was merged, promoted, retired,
and what the user ruled on for contradictions.
```

## example entries

```md
## active rules
- state the point first; no dramatic buildup (standing law, given 3x: 06-02, 06-05, 06-11)
- preserve rough edges; "too polished" is a rejection, not a compliment

## raw feedback log
### 2026-06-11
raw: "too polished. i don't talk like that"
rule: preserve rough edges; do not smooth casual phrasing into clean copy
patched: voice.md (fake-polish bans), anti-slop.md

## retired / stale rules
- "no threads while the account is small" (2026-04) — retired 2026-06, account crossed the size the rule was scoped to

## distillation log
### 2026-06-12
merged 3 buildup-cadence entries into one standing law; promoted it to anti-slop.md; no contradictions
```

## cadence

- **append** the raw correction to the raw feedback log after every feedback event — dated, verbatim
- **distill** every 10 entries or weekly/monthly: merge duplicates, promote recurring corrections into active rules, decay stale context into retired
- **split** when the file gets too long to read in a couple of minutes — the four sections are already the split
- **contradictions require user review** — never resolve two conflicting rules silently; surface both with dates, let the user rule, log it in the distillation log

## update rule

Append on every correction, newest first in the raw feedback log, always dated, always with the raw quote. When a rule recurs, promote it into active rules and to judgment.md/anti-slop.md. Newer rules beat older ones in conflicts — record the supersession in retired/stale rather than deleting. Run distillation on cadence so volume never becomes noise.
