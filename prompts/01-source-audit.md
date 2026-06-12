# 01 — source audit

Goal: know what material exists, what it can teach you, and what's missing — before reading anything deeply.

## Checklist — ask the user which of these they have

- [ ] exported Claude conversations (claude.ai export, or Claude Code session files)
- [ ] ChatGPT exports (settings → data controls → export)
- [ ] Cursor sessions / composer history
- [ ] Hermes sessions or logs
- [ ] notes (markdown folders, Obsidian vaults, Apple Notes dumps, Notion exports)
- [ ] docs (briefs, scripts, plans, READMEs they wrote)
- [ ] tweets/posts (their own, exported or pasted)
- [ ] scripts (video scripts, talk outlines)
- [ ] drafts — especially ones they abandoned
- [ ] rejected outputs — AI work they threw away (gold)
- [ ] references — work by others they love, with why
- [ ] feedback messages — corrections they gave to AI or collaborators ("too polished", "not me", "this is cringe")

## For each source the user names

Record:

```
source: <path or description>
type: <conversation export / notes / posts / drafts / rejected / feedback / references>
era: <roughly when>
likely yields: <voice / taste / judgment / context / lexicon / anti-slop>
```

## Rules

- Read only what the user points you at. Never expand the scan on your own.
- If you hit secrets, tokens, client data, or private DMs: skip them, flag to the user, do not copy into any output.
- Rank sources by contrast value: rejected outputs and feedback first, then their own writing, then references, then generic notes.
- If they have zero rejected outputs or feedback, ask for two or three examples of AI output they disliked and one sentence each on why. That alone seeds judgment.md and anti-slop.md.

## Output of this step

Present the user a short audit summary: what you have, what each source will likely yield, what's missing, and the proposed scan list. **Get their confirmation before deep reading.**
