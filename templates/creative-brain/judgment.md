# judgment.md — template

## purpose

The user's decision rules — how they call good / weak / too safe / too much / not me. Voice is how they sound; judgment is how they decide. This file is what lets an agent self-review before showing work.

## what belongs here

- explicit quality bars ("done means…")
- the user's own evaluative vocabulary, verbatim (what do *they* call things: "cringe", "flat", "try-hard", "dead")
- kill rules: conditions under which work gets rejected regardless of polish
- trade-off rulings they've made (speed vs polish, clarity vs cleverness, safe vs loud)
- self-review questions to run before finalizing anything

## what does not belong here

- banned words/structures (anti-slop.md)
- the failed outputs themselves (rejected-examples.md — link to entries instead)
- your own quality opinions as the agent

## suggested sections

```md
## quality bar
## their evaluative vocabulary
## kill rules
## trade-off rulings
## pre-final checklist
```

## example entries

```md
## kill rules
- if it could appear under anyone's name unchanged, it dies — no matter how clean
- explains the joke = dead on arrival

## their evaluative vocabulary
"cringe" = trying to perform a feeling instead of having one (see rejected-examples #3)
```

## update rule

Append a rule every time the user accepts or rejects something and the reason generalizes. Link each kill rule to a rejected-example entry when one exists. Promote twice-given corrections from feedback-memory.md into standing rules here.
