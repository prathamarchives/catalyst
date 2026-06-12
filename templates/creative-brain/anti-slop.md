# anti-slop.md — template

## purpose

Everything banned: words, phrases, structures, cadences, vibes, formats. This file exists so the agent can kill failure modes *before* the user has to. It is allowed — required — to contain the banned phrases themselves; that's its job.

## signal hierarchy

**Annotated rejected examples with reasons outrank generic banned-word lists.** Everyone bans the same startup-vapor words now; a word list says little about *this* user. Banned words are fallback guardrails — the real signal lives in rejected-examples.md: the bad output itself, why the user killed it, what a better output would preserve, and what rule it teaches. When this file and a rejected example disagree about what's slop for this user, the example wins. Keep the word table, but spend the effort on the examples.

## what belongs here

- banned words and phrases, listed plainly in a table
- banned structures (e.g., dramatic buildup chains, "not X but Y" scaffolds, listicle cadence)
- banned vibes (corporate enthusiasm, fake humility, motivational-poster energy)
- banned formats/tropes the user mocks
- the reason each ban exists, if known — bans with reasons survive; arbitrary bans get violated

## what does not belong here

- positive style guidance (voice.md, taste.md)
- one-off corrections not yet generalized (feedback-memory.md until they recur)

## suggested sections

```md
## banned words and phrases
## banned structures
## banned vibes
## why these bans exist
```

## example entries

```md
## banned words and phrases
| banned | why |
|---|---|
| unlock | startup vapor; means nothing |
| supercharge | same |
| all-in-one | claims everything, promises nothing |
| revolutionize | the word that has never once been true |

## banned structures
- "not because X. not because Y. because Z." — movie-trailer cadence
- ending with a fake punchline ("that's the game.")
```

## update rule

Append on every recurrence: when a correction in feedback-memory.md happens twice, the offending word/structure gets promoted here. Never delete a ban without explicit user approval — bans are hard-won.
