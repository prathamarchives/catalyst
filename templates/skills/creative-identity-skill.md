# creative-identity skill — template

This is the master template for the generated skill. Agents: copy and customize into `outputs/<name>/skills/creative-identity-skill.md`. A generated skill that still reads like this template is a failed generation — the "this user specifically" and "red flags" sections must be filled with the actual user's rules.

---

# <User/Project> Creative Identity Skill

brain location: `../creative-brain/` (relative to this file)

## when to use

Use before writing, designing, editing, researching, ideating, replying, or planning creative work for <user/project>. If the task touches anything the user will put their name on, load the brain first.

## load order

1. identity.md — who they are, what they are not
2. context.md — what's live right now (check the `updated:` date)
3. voice.md — how they sound
4. taste.md — what they like, by contrast
5. judgment.md — how they decide
6. anti-slop.md — what is banned
7. feedback-memory.md — standing laws + recent corrections
8. rejected-examples.md — what failure looks like

## operating rules

- use the user's raw language as source, not decoration
- preserve taste and judgment over generic fluency
- act from observed behavior, not just stated preference — when they conflict, behavior wins
- check rejected examples before finalizing anything
- if output feels generic, stop and ask what context is missing — do not ship "averaging the internet"
- after feedback, update feedback-memory.md and any affected brain file
- when rules conflict, newer beats older; ask the user if it matters

## compounding (session to session)

This brain is not static. It should be sharper every session than the last:

- every session the user runs with this brain loaded is new source material — new corrections, new phrases, new behavior
- at the end of a working session, fold what you learned back into the brain: new feedback into feedback-memory.md, new patterns into voice/taste/judgment, new operating behavior into the relevant file
- periodically re-discover recent sessions (tools/discover_sessions.py) and ingest them — the brain compounds from how the user keeps working, not just the one-time build
- a correction given twice is a standing law; promote it

## this user specifically

<3–8 rules unique to this user, distilled from their brain. The things a fresh agent gets wrong about them first. Example shape:
- opens with the contradiction, never with a definition
- lowercase in posts, normal case in docs
- one concrete receipt beats three adjectives>

## feedback loop

When the user says: keep this / more like this / less like this / this is cringe / not me / closer / too polished / too generic —

1. capture the raw quote
2. extract the rule
3. append to feedback-memory.md (dated)
4. patch the affected brain file
5. if it changes operating behavior, update this skill

## red flags

<the user's fastest tells that an output is off, pulled from anti-slop.md and rejected-examples.md. Example shape:
- enthusiasm performance ("thrilled to announce")
- dramatic buildup before the point
- could appear under anyone's name unchanged>
