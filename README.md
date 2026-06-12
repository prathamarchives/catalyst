# creative-identity

An open-source repo your agent can run to build your Creative Brain.

Paste it into Claude Code, Cursor, Hermes, or any agent. It discovers your past AI sessions, notes, and project workspaces across your machine — you don't hunt for files — then, with your approval of the scope, scans them and extracts how you talk, what you like, what you reject, your context, taste, standards, behavior, and feedback patterns. Then it writes a skill your agent loads to keep getting sharper every session you use it.

> Your agent doesn't need another prompt. It needs your creative identity.

Same model. Different brain.

## What is this?

Everyone has access to the same intelligence now. Models keep getting stronger and cheaper. Output is abundant. The edge is not the model — it is the context, taste, judgment, feedback, rejected examples, and memory around the model.

`creative-identity` turns your messy context into agent-readable taste, memory, and judgment. It is:

- **a protocol** ([AGENTS.md](AGENTS.md)) that any agent can execute
- **a set of prompts** ([prompts/](prompts/)) that walk the agent through discover → audit → interview → extraction → build → proof → feedback
- **a discovery helper** ([tools/discover_sessions.py](tools/discover_sessions.py)) that finds your AI sessions and workspaces across the system, read-only
- **templates** ([templates/](templates/)) for the ten Creative Brain files, a generated skill, five workflows, and a blind A/B log
- **an eval harness** ([evals/](evals/)) that keeps the repo itself honest

It is not a web app. There are no accounts, no hosted service, no analytics UI, no required API keys. It is a repo-as-product: markdown-first, local-first, agent-runnable.

## Who is it for?

Agent-native creators, operators, and builders who already use AI and have messy source material: old sessions, posts, scripts, notes, drafts they killed, feedback they gave. If you can hand a repo to an agent and read markdown, this is for you.

## Why does it exist?

Because an agent that doesn't know your taste, context, and standards averages the internet. It produces competent, generic work that belongs to nobody. More prompting doesn't fix that — you can't fit your whole brain into a prompt every time, and whatever you teach it evaporates at the next session.

The fix is a brain the agent can load: who you are, how you talk, what you like, what you reject, and every correction you've ever given — stored as files, compounding over time.

## How do I install it?

Give your agent the repo link and one sentence:

```txt
https://github.com/prathamarchives/creative-identity
help me install this and build my Creative Brain
```

There is no package install — this is a markdown protocol, not an app, so there's no `package.json` / `requirements.txt` to install and no dependencies. "Install" means clone/open the repo, optionally verify it (`py evals/run_all.py`), and then run setup. A correct agent does not stop at clone: it rolls straight into discovering your sources, recommending a safe scan scope, and building the brain. Full install flow: [INSTALL.md](INSTALL.md). Copy/paste setup prompts (autonomous, cautious, manual): [SETUP-PROMPT.md](SETUP-PROMPT.md).

## How do I use it?

If you'd rather drive it yourself, clone this repo, open it with your agent, and paste the prompt from [REPO-USE-PROMPT.md](REPO-USE-PROMPT.md). Variants exist for Claude Code, Cursor, Hermes, and any generic agent. The difference between install, verify, and use: [docs/install-vs-use.md](docs/install-vs-use.md).

The short version:

```
Read README.md and AGENTS.md. Use this repo to build my Creative Brain.
First discover where my AI sessions, notes, exports, and workspaces live.
Do not read file contents yet. Show me the discovered locations and ask what you may scan.
Audit only the approved scope, interview me in small rounds, create files under outputs/<name>/,
write a creative-identity skill, run a before/after proof, then ask for feedback
and update the system so it compounds session to session.
```

The agent's first action is always the same: discover where your AI sessions and workspaces live, show you the list, and ask which it may scan. It never starts by writing content.

## What source material does it use?

The discovery step finds most of it for you. It looks across the system for:

- Claude Code sessions (`~/.claude/projects`), Cursor / VS Code chat history, Codex / Copilot / Gemini CLI state
- exported Claude / ChatGPT conversations in Downloads
- notes (Obsidian vaults, Notion exports), docs, journals
- project workspaces under Desktop / Documents — your real working folders
- and from all of it: how you talk, what you reject, your behavior across sessions

It shows you everything it found and reads only the scope you approve. You can also point it at anything it missed. More contrast (rejected drafts, feedback) beats more volume. See [prompts/01-source-audit.md](prompts/01-source-audit.md) for the discovery + audit flow.

## What files does it create?

Everything lands under `outputs/<your-name-or-project>/`:

```
outputs/<name>/
  creative-brain/
    identity.md          who you are, what you're building, what you're not
    context.md           live projects, goals, audience, constraints
    voice.md             how you actually talk, with evidence quotes
    taste.md             what you like and notice, by contrast
    judgment.md          your decision rules: good / weak / too safe / too much
    anti-slop.md         banned words, structures, vibes
    references.md        what to learn from each reference, what not to copy
    rejected-examples.md outputs that failed and why — the gold file
    feedback-memory.md   every correction, distilled into durable rules
    lexicon.md           your words, phrases, shorthand, mission lines
  skills/
    creative-identity-skill.md   the reusable skill future agents load
  workflows/
    use-creative-brain.md
    update-from-feedback.md
    review-output.md
    blind-ab-test.md
    distill-memory.md
  evals/
    blind-ab-log.md      blind preference results + running win-rate
  examples/
    before-after.md      the proof artifact
```

Templates are never overwritten — they stay pristine in `templates/` so you can re-run the protocol any time.

## How does feedback improve the Creative Brain?

Every correction you give ("keep this", "less like this", "too polished", "not me") becomes a durable rule in `feedback-memory.md`, and the affected brain file gets patched. The generated skill tells future agents to load that memory before any creative work — so the system gets sharper with use instead of resetting. See [prompts/07-update-from-feedback.md](prompts/07-update-from-feedback.md).

Memory is maintained, not just appended: append-only memory rots over months. A periodic distillation pass merges duplicate rules, promotes recurring corrections to standing laws, decays stale context, and surfaces contradictions for your review. See [docs/memory-lifecycle.md](docs/memory-lifecycle.md) and [prompts/09-distill-and-decay-memory.md](prompts/09-distill-and-decay-memory.md).

## How do I run the before/after proof?

Ask the agent to run [prompts/06-run-before-after-proof.md](prompts/06-run-before-after-proof.md). It takes one real task, produces a generic baseline without the Creative Brain, then the same task with the brain loaded, and writes `before-after.md` documenting the task, both outputs, what changed, your feedback, and the memory update. That artifact is the point: same model, different brain, visible difference.

A worked example lives at [examples/pratham-mini/before-after.md](examples/pratham-mini/before-after.md). Two honesty rules: the generic baseline must be competent — the best cold version, not a strawman — and the before/after is the demo, not the measurement. For an unbiased measurement, run the blind A/B proof ([prompts/10-run-blind-ab-proof.md](prompts/10-run-blind-ab-proof.md)): labels hidden and shuffled, you pick a winner blind, and the result feeds a running `brain_win_rate` plus an effectiveness log (did the post land, did the DM get a response). See [docs/blind-ab-eval.md](docs/blind-ab-eval.md).

## What is local/private by default?

- **local-first**: everything runs on your machine, in your files.
- **you control the scan**: discovery finds candidate locations automatically, but the agent reads contents only inside the scope you approve — never beyond it. Discovery checks that paths exist; it reads nothing until you say yes.
- **no cloud upload by default**: this protocol makes no network calls and requires no API keys. The discovery helper is read-only and offline.
- **outputs are gitignored**: `outputs/**` is excluded by default, so your brain never lands in a public commit unless you deliberately choose to share it.
- **your responsibility**: don't approve scopes containing secrets, tokens, client data, or private DMs unless you intend the brain to contain them. Review files before sharing.
- **agent/model caveat**: this repo itself makes no network calls, but the agent/model you use may send approved context to its provider. Check your tool's privacy policy before approving sensitive material.

Full stance: [docs/privacy.md](docs/privacy.md).

## How do I run evals?

The repo ships with a deterministic eval harness (Python standard library only, no LLM calls):

```
python evals/run_all.py
```

On Windows, if `python` isn't wired up, use the launcher:

```
py evals/run_all.py
```

It checks structure, banned-phrase hygiene, protocol completeness, privacy language, the example proof, and static agent-runnability. Exit code 0 means all pass. Results from the last run are in [EVAL_REPORT.md](EVAL_REPORT.md), and the loop philosophy is in [docs/eval-loop.md](docs/eval-loop.md).

## Roadmap

- **v0** — this repo: markdown protocol + eval harness
- **v0.1** — stronger worked examples
- **v0.2** — export guides for Claude / ChatGPT / Cursor / Hermes sessions
- **v1** — optional tiny local CLI (scaffold outputs, run checks)
- **v2** — Catalyst product layer, only after repeated manual proof

Details: [docs/roadmap.md](docs/roadmap.md).

## License

MIT. See [LICENSE](LICENSE).
