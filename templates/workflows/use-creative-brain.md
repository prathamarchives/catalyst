# workflow — use the creative brain

For any agent about to do creative work for this user. This is the default operating loop once a brain exists.

## steps

1. **Load the skill** — `skills/creative-identity-skill.md`. It sets the load modes and the user-specific rules.
2. **Pick a load mode and load the brain.** Quick mode (identity, voice, anti-slop, feedback-memory) for replies, edits, fast DMs, tone checks. Full mode (the whole brain, in order) for posts, strategy, landing pages, positioning — anything public-facing. Check context.md's `updated:` date; if stale, confirm what's live before proceeding. When a quick task starts touching positioning, escalate to full mode.
3. **Restate the task** through the brain: who is this for, what surface, which voice register applies.
4. **Draft** from the user's world — their phrases (lexicon), their openings (voice), their quality bar (judgment).
5. **Self-review before showing anything:**
   - run judgment.md's pre-final checks
   - scan against anti-slop.md bans
   - compare against rejected-examples.md — does this resemble anything that died?
   - the ownership test: could this appear under anyone's name unchanged? if yes, it's not done
6. **Show the work** with one line on which brain rules drove the big choices (helps the user correct the rule, not just the output).
7. **Collect feedback** and run [update-from-feedback.md](update-from-feedback.md).

## rules

- never skip the self-review; the brain exists so failures die before the user sees them
- if the brain is silent on something important, ask — then record the answer so it's never asked again
- thin output usually means thin context: go back to the brain before going back to the draft
