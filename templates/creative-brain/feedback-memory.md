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

## suggested sections

```md
## standing laws (corrections given 2+ times)
## entries (newest first)
### <date>
raw: "<verbatim user words>"
rule: <the generalized preference>
patched: <which files were updated>
```

## example entries

```md
## standing laws
- state the point first; no dramatic buildup (given 3x: 06-02, 06-05, 06-11)

## entries
### 2026-06-11
raw: "too polished. i don't talk like that"
rule: preserve rough edges; do not smooth casual phrasing into clean copy
patched: voice.md (fake-polish bans), anti-slop.md
```

## update rule

Append on every correction, newest first, always dated, always with the raw quote. When an entry's rule recurs, promote it to standing laws and to judgment.md/anti-slop.md. Newer rules beat older ones in conflicts — record the supersession rather than deleting.
