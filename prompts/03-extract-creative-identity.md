# 03 — extract the creative identity

Goal: turn the audited material + interview answers into structured findings for the ten brain files. This is analysis, not writing-for-the-user.

## Extraction targets

For each target, collect patterns **with evidence quotes** from the user's actual material:

| target | what you're looking for |
|---|---|
| identity | who they are, what they're building, what world they orbit, what they are NOT |
| context | live projects, goals, audience, offers, constraints, current priorities |
| voice | rhythm, openings, sentence length, casing, slang, how they argue, how they joke |
| taste | what they praise, what they return to, what they notice first, quality markers |
| judgment | their decision rules: what makes something good / weak / too safe / too much — applied across creative, coding, workflow, and strategy work, not just content |
| behavior | how they actually work across sessions: how they open, what they kill, how they react to feedback, their operating patterns — observed, not self-described |
| craft / workflow | coding and workflow preferences, tools and conventions they reach for, how they like to drive an agent (terse vs detailed, plan-first vs ship-first), what they delegate vs control |
| anti-slop | words, structures, vibes, formats they reject or mock |
| references | who/what they admire — with "what to learn" and "what not to copy" per reference |
| rejected examples | actual outputs they killed, verbatim, with the failure reason |
| feedback patterns | corrections they give repeatedly — these become standing rules |
| lexicon | their words: phrases, shorthand, jokes, metaphors, mission lines |

## Evidence rule

Every significant claim needs a quote:

```
pattern: <the pattern you observed>
evidence: "<verbatim quote from their material>"
source: <which file/conversation it came from>
```

## Observed vs assumed

Mark every finding:

- `observed` — you have a quote or direct interview answer.
- `assumed` — you're inferring. Assumptions must be confirmed with the user in a quick round, or cut. **Unconfirmed assumptions never ship in the brain.**

## Extract taste by contrast

Likes alone are weak signal. For every "likes X", hunt for the matching "rejects Y". The pairs are the taste. Rejected examples with reasons are worth more than any amount of positive description.

**Annotated rejected examples with reasons outrank generic banned-word lists.** Banned-word tables converge on the same genre hygiene for everyone; they are fallback guardrails, not identity. The high-signal extraction is the killed output itself, why the user killed it, what a better output would have preserved, and what rule it teaches. Given an hour, spend fifty minutes on rejected-examples.md and ten on the word table.

## Extract behavior from sessions, not just statements

Past AI sessions and workspaces are a behavior record. Mine them for how the user *actually operates*, which is often different from how they describe themselves:

- how they open a task; what they ask for first
- what they reject, and how fast — the corrections they repeat
- how they react under feedback (do they tighten, expand, kill?)
- their working rhythm: loose vs precise, where they slow down, what they delegate
- the gap between what they say they want and what they keep

Behavior observed across many sessions outranks any single self-description. When the user says "I like X" but every session shows them killing X, the behavior wins — note the contradiction for the interview.

## Preserve raw language

When the user's own phrasing is alive ("this is cringe", "sounds like a press release", "averaging the internet"), keep it verbatim. Do not translate them into neutral professional English — that translation is exactly the loss this system prevents.

## Output of this step

A findings document (working notes, not yet the brain) organized by the ten targets, every claim tagged observed/assumed, with evidence quotes. Show the user the assumed list for confirmation before building.
