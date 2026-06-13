# 04 — build the creative brain

Goal: turn confirmed extraction findings into the ten brain files.

## Where files go

```
outputs/<user-or-project>/creative-brain/
  identity.md
  context.md
  voice.md
  taste.md
  judgment.md
  anti-slop.md
  references.md
  rejected-examples.md
  feedback-memory.md
  lexicon.md
```

Agree on `<user-or-project>` with the user. **Never overwrite templates** — `templates/creative-brain/` stays pristine; you copy its structure, not its files.

## Build rules

1. Use each template in `templates/creative-brain/` as the blueprint for sections and update rules.
2. Fill every file with real extracted material. **No placeholder text in a generated brain.** If a file has thin material, say so explicitly inside the file ("seed only — needs more rejected examples") rather than padding it.
3. Keep evidence quotes inline where they carry weight (voice, taste, judgment).
4. Keep the user's raw language. The brain should sound like them, not like documentation about them.
5. rejected-examples.md and feedback-memory.md are living files — structure them so future entries are cheap to add (dated entries, consistent format).
6. Cross-link files where it helps (e.g., a judgment rule that references a rejected example).
7. End each file with its update rule (when and how future agents should append to it — the templates specify this).

## Also create

The full output folder — this list must match the output structure in [AGENTS.md](../AGENTS.md):

```
outputs/<name>/
  skills/catalyst-skill.md   (written in step 05)
  workflows/                          (copy ALL FIVE from templates/workflows/, customize user-specific steps)
    use-creative-brain.md
    update-from-feedback.md
    review-output.md
    blind-ab-test.md
    distill-memory.md
  evals/blind-ab-log.md               (copy from templates/evals/blind-ab-log.md — initializes the blind A/B scoreboard)
  examples/before-after.md            (written in step 06)
  README.md                           (one short paragraph: whose brain, when built, from what sources, how to load it)
```

Copy all five workflows, not three — `blind-ab-test.md` and `distill-memory.md` are part of the standard set now. Initialize `evals/blind-ab-log.md` from its template so the blind A/B scoreboard exists from day one even before the first test.

## Quality gate before moving on

- All ten creative-brain files exist and contain real material
- No template placeholders left
- Raw user language visible in voice/lexicon/feedback files
- At least one real entry in rejected-examples.md
- All five workflows copied into `outputs/<name>/workflows/`
- `outputs/<name>/evals/blind-ab-log.md` initialized
- The user has seen the file list and skimmed at least voice.md and anti-slop.md
