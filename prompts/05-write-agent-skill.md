# 05 — write the agent skill

Goal: generate `outputs/<name>/skills/creative-identity-skill.md` — the reusable skill that teaches any future agent to create from this user's brain and keep improving it.

This is the most important output of the whole protocol. The brain is data; the skill is the behavior.

## Use the template as the skeleton

Start from `templates/skills/creative-identity-skill.md` (do not modify the template itself). Customize every section with this user's actual rules — a skill that could belong to anyone is a failed skill.

## Required sections

```md
# <User/Project> Creative Identity Skill

## when to use
Use before writing, designing, editing, researching, ideating, replying,
or planning creative work for <user/project>.

## load order
1. identity.md
2. context.md
3. voice.md
4. taste.md
5. judgment.md
6. anti-slop.md
7. feedback-memory.md
8. rejected-examples.md

## operating rules
- use the user's raw language as source, not decoration
- preserve taste and judgment over generic fluency
- check rejected examples before finalizing anything
- if output feels generic, stop and ask what context is missing
- after feedback, update feedback-memory.md and any affected file

## this user specifically
<3-8 rules unique to this user, distilled from their brain — the things
a fresh agent gets wrong about them first>

## feedback loop
When the user says: keep this / more like this / less like this /
this is cringe / not me / closer / too polished / too generic —
extract the rule and patch the relevant Creative Brain file.

## red flags
<the user's fastest tells that an output is off — pulled from
anti-slop.md and rejected-examples.md>
```

## Rules

- The "this user specifically" section is the value. Generic operating rules plus zero personal rules = template copy, not a skill.
- Include one or two evidence quotes in the skill so future agents hear the user's actual register immediately.
- Keep it loadable: under ~2 pages. The skill points to the brain files; it doesn't duplicate them.
- Tell the agent reading the skill where the brain lives (relative path).
