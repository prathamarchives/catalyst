# 05 — write the agent skill

Goal: generate `outputs/<name>/skills/creative-identity-skill.md` — the reusable skill that teaches any future agent to create from this user's brain and keep improving it.

This is the most important output of the whole protocol. The brain is data; the skill is the behavior.

## Use the template as the skeleton

Start from `templates/skills/creative-identity-skill.md` (do not modify the template itself). Customize every section with this user's actual rules — a skill that could belong to anyone is a failed skill.

## Required sections

The generated skill must include all of these — `output_consistency_check` enforces the load-mode sections specifically:

```md
# <User/Project> Creative Identity Skill

## when to use
Use before writing, designing, editing, researching, ideating, replying,
or planning creative work for <user/project>.

## load modes
Pick by stakes, not habit.

### quick mode
identity.md, voice.md, anti-slop.md, feedback-memory.md
— for short replies, lightweight edits, fast DMs, one-shot tone checks.

### full mode
identity, context, voice, taste, judgment, anti-slop, references,
rejected-examples, feedback-memory, lexicon (full load order)
— for strategy, public posts, landing pages, deep writing, offer
positioning — anything that affects public identity or product direction.

## operating rules
- use the user's raw language as source, not decoration
- preserve taste and judgment over generic fluency
- check rejected examples before finalizing anything
- if output feels generic, stop and ask what context is missing
- after feedback, update feedback-memory.md and any affected file

## compounding (session to session)
Every session run with this brain is new source material; fold corrections,
phrases, and behavior back in so the brain is sharper each session, not reset.

## blind A/B scoreboard
Run the blind-ab-test workflow on real tasks; track brain_win_rate over time
in outputs/<name>/evals/blind-ab-log.md. A stalling rate = run distillation.

## memory lifecycle
Append corrections immediately; distill periodically (merge duplicates,
promote standing laws, decay stale context, surface contradictions to the user).

## feedback loop
When the user says: keep this / more like this / less like this /
this is cringe / not me / closer / too polished / too generic —
extract the rule and patch the relevant Creative Brain file.

## this user specifically
<3-8 rules unique to this user, distilled from their brain — the things
a fresh agent gets wrong about them first>

## red flags
<the user's fastest tells that an output is off — pulled from
anti-slop.md and rejected-examples.md>
```

## Rules

- The "this user specifically" section is the value. Generic operating rules plus zero personal rules = template copy, not a skill.
- Include one or two evidence quotes in the skill so future agents hear the user's actual register immediately.
- Keep it loadable: under ~2 pages. The skill points to the brain files; it doesn't duplicate them.
- Tell the agent reading the skill where the brain lives (relative path).
