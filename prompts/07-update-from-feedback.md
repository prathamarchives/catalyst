# 07 — update from feedback

Goal: turn every user correction into durable memory. This step is why the system compounds instead of resetting.

## When to run

Every time the user reacts to an output: during the proof, and any time afterward. Reactions that count:

- keep this / more like this
- less like this / not me / this is cringe
- too polished / too generic / too safe / too much
- closer / almost / the second half works
- any rewrite they do themselves (their rewrite is the strongest signal you'll ever get)

## Procedure

1. **Capture the raw correction verbatim.** Their phrasing is data — "sounds like LinkedIn" is a better rule seed than "tone mismatch".

2. **Extract the underlying rule.** Ask: what general preference does this correction reveal, beyond this one output?

```
raw: "why is every sentence so dramatic, just say the thing"
rule: no dramatic buildup structures; state the point first, plainly
applies to: voice.md (rhythm), anti-slop.md (banned structure)
```

3. **Append to feedback-memory.md** with date, raw quote, distilled rule, and which files were patched.

4. **Patch the affected brain files.** A rule that only lives in feedback-memory and never reaches voice/taste/judgment/anti-slop will get missed by future agents.

5. **Update the generated skill** if the correction changes operating behavior (e.g., a new red flag, a new check before finalizing).

6. **If they rewrote your output:** diff your version against theirs. Every change they made is a pattern candidate — openings, cuts, word swaps, structure. Extract at least one rule from the diff.

## Rules

- Never argue with feedback in the memory file. Record it, distill it, apply it.
- Contradictions with existing rules are signal, not noise: note both, ask the user which wins, record the resolution.
- Date every entry. Newer rules beat older rules when they conflict.
- A correction given twice is a standing law — promote it prominently (top of anti-slop.md or the skill's red flags).
