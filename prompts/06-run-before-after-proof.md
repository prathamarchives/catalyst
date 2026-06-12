# 06 — run the before/after proof

Goal: make "same model, different brain" visible with one real task. This artifact is the verification of the whole build — and the thing the user can show others.

## Procedure

1. **Pick the task with the user.** One real creative task they actually need: a post, a reply, a product blurb, a title set, an outline. Real beats hypothetical.

2. **Generic output (before).** Do the task with NO Creative Brain context. No brain files, no user quotes, no style notes — just the task, the way any agent would do it cold. Do not sandbag it: write the genuinely best generic version. The proof only counts if the baseline is honest.

3. **Creative Brain output (after).** Load the full brain per the generated skill (load order matters). Do the same task again, acting from the user's voice, taste, judgment, anti-slop rules, and feedback memory. Check rejected-examples.md before finalizing.

4. **Document it** in `outputs/<name>/examples/before-after.md`:

```md
# before/after proof — <date>

## task
<the exact task, one or two lines>

## generic output
<the cold version, verbatim>

## creative brain output
<the brain-loaded version, verbatim>

## what changed
<specific, named differences: openings, vocabulary, structure, claims,
what was cut, what was added, which brain files drove which change>

## user feedback
<their verbatim reaction — collected after showing both>

## feedback memory update
<the rules extracted from that feedback and where they were written>
```

5. **Show the user both outputs side by side.** Ask: keep / cut / rewrite / more-like / less-like — per piece, not just overall.

6. **Run the feedback update** ([07-update-from-feedback.md](07-update-from-feedback.md)) on whatever they say, and fill in the last two sections of the proof file.

## Rules

- "What changed" must name mechanisms, not vibes. "Opens with the user's contradiction pattern instead of a definition" — not "feels more authentic".
- If the two outputs are barely different, the brain is thin. Say so, and go collect more contrast material (rejected examples, feedback) instead of faking a difference.
- One task is enough for v0. Depth beats coverage.
