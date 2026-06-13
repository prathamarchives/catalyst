# permission model

What the agent may do on its own, and what needs your explicit yes. The goal is minimal burden: the agent handles the mechanical work and stops only at the few points where your judgment or trust is actually required.

## the four things only you can decide

1. **scan scope** — which discovered locations the agent may read
2. **interview gaps** — answering small questions when sources don't cover something
3. **taste feedback** — reacting to outputs so the brain learns
4. **destructive / external actions** — anything that deletes, sends, or publishes

Everything else is the agent's job.

## action table

| action | risk | explicit approval? | fallback |
|---|---|---|---|
| clone / open the repo | low | no — implied by "install this" | tell the user the path it cloned to |
| read the repo's own markdown | none | no | — |
| run the eval harness (`py evals/run_all.py`) | low (runs local stdlib code) | no, but announce it | if blocked by a classifier, say so and continue; verification is optional |
| run `tools/discover_sessions.py` | low (read-only, paths only) | no, but announce it | if it can't run, discover by listing known locations manually |
| read the user's source files | medium (private content) | **yes — authorized up front (Mode A) or one scope approval (Mode B)** | manual mode: user names exact paths |
| write to `outputs/<name>/` | low (local, gitignored) | no | confirm the folder name with the user once |
| send approved context to the model provider | medium (leaves the machine) | implied by using a hosted agent — **flag it** | warn before approving sensitive material; use a local model if required |
| commit the generated brain | medium (could expose private content) | **yes** | `outputs/**` is gitignored by default; leave it uncommitted unless asked |
| push to GitHub | high (publishes) | **yes — always** | never push without an explicit request |
| delete files / folders / repos | high (irreversible) | **yes — always** | propose; never delete on your own initiative |

## reading is authorization-gated; discovery is not

Discovery only checks that paths **exist** — it reads no contents and sends nothing. So the agent may discover freely. **Reading** the contents of those locations is what needs authorization, because that's where private material actually gets opened. Authorization comes in one of two modes:

- **autonomous authorized mode (Mode A):** the user's opening prompt already authorized the recommended safe scan. The agent states the scope and proceeds — no second approval question.
- **cautious approval mode (Mode B):** authorization is ambiguous, so the agent asks exactly one question before reading:
  > Approve recommended scan, edit scope, or manual mode?

In both modes the agent reads only inside the authorized scope, and the exclusions (secrets/client/DMs/sensitive) always bind. Authorization can skip the question; it can never skip the exclusions.

## the model-provider caveat

This repo makes no network calls. But the agent you run it with usually does — a hosted model sees whatever context you approve. The repo can't control your tool's provider. Before approving sensitive material (client data, private DMs, secrets), check your tool's privacy policy, or run a local model. If the agent encounters secrets/tokens/client data/private DMs while scanning, it skips them and flags them — it does not copy them into the brain. See [docs/privacy.md](privacy.md).

## default posture

When unsure, the agent should: prefer read-only, prefer the smallest scope that does the job, announce code it's about to run, and never take a high-risk action (push, delete, send) without an explicit yes. Low-risk mechanical steps it just does — asking permission for every file write is its own kind of burden.
