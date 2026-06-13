# install vs verify vs use

Three different things people mean by "install this repo." Keeping them straight is what stops an agent from cloning the repo and then standing around asking what to do.

```
install = get the protocol ready   (clone/open the repo; no package step)
verify  = run the evals            (optional; confirms the repo is intact)
use     = run the protocol         (discover → approve → build the Creative Brain)
```

## install — get the protocol ready

There is no package manager step. Cloning or opening the repo *is* the install. No `npm install`, no `pip install`; the absence of `package.json` / `requirements.txt` is expected. Once the files are present, install is complete — and you immediately move to use. Install is not a stopping point.

## verify — run the evals (optional)

`py evals/run_all.py` checks the repo is structurally intact and the protocol is consistent. Exit `0` means good. This is optional confidence, not a gate: if it's blocked by a permission classifier, say so and continue. Verification failing to run never means "install failed."

## use — run the protocol

This is the actual work and where almost all the value is: discover the user's source locations, recommend a safe scan scope, get authorization (already given in the prompt under autonomous authorized mode, or one approval question under cautious approval mode), scan only that scope, build `outputs/<name>/`, write the skill, run the proof, and compound from feedback. Driven by [prompts/08-install-and-run.md](../prompts/08-install-and-run.md) and the rest of `prompts/`.

## bad / good

**Bad — stops at clone:**

> Bad: I cloned it. There's no package.json, so there's nothing to install. Want me to do anything else?

**Good — install flows straight into use:**

> There is no package install. This is a protocol repo, so install is complete. Next I'll run setup: discover sources, recommend a scan scope, ask approval, build the brain, write the skill, and run proof.

**Bad — dumps path management on the user:**

> Bad: I found these 47 folders. Which ones should I scan?

**Good — recommends a scope, one question:**

> I found AI sessions, exports, notes, and workspaces. I recommend the safe scan: AI sessions + exports + markdown-heavy workspaces, excluding secrets/client/private-DM/vendor/build/binary folders. Approve recommended scan, edit scope, or manual mode?

**Bad — makes the user be the discovery tool:**

> Bad: Where are your Claude sessions? Where are your Cursor sessions? Where are your notes?

**Good — discovers first, then confirms:**

> I'll discover common session/export/workspace locations first, then ask for approval before reading contents. If I miss something, you can add it.

## the rule

Install and verify are quick and mostly invisible. Use is the protocol. An agent that finishes install and then waits for instructions has misunderstood the repo — install is supposed to roll directly into use, pausing only for the one scan approval.
