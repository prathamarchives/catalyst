# creative-identity

An open-source repo your agent can run to build your Creative Brain.

Point Claude Code, Cursor, Hermes, or any agent at your exported sessions, notes, drafts, references, and feedback. It will extract how you talk, what you like, what you reject, your context, taste, standards, and feedback patterns — then write a skill your agent can use to keep improving as you use it.

> Your agent doesn't need another prompt. It needs your creative identity.

Same model. Different brain.

## What is this?

Everyone has access to the same intelligence now. Models keep getting stronger and cheaper. Output is abundant. The edge is not the model — it is the context, taste, judgment, feedback, rejected examples, and memory around the model.

`creative-identity` turns your messy context into agent-readable taste, memory, and judgment. It is:

- **a protocol** ([AGENTS.md](AGENTS.md)) that any agent can execute
- **a set of prompts** ([prompts/](prompts/)) that walk the agent through audit → interview → extraction → build → proof → feedback
- **templates** ([templates/](templates/)) for the ten Creative Brain files, a generated skill, and three workflows
- **an eval harness** ([evals/](evals/)) that keeps the repo itself honest

It is not a web app. There are no accounts, no hosted service, no analytics UI, no required API keys. It is a repo-as-product: markdown-first, local-first, agent-runnable.

## Who is it for?

Agent-native creators, operators, and builders who already use AI and have messy source material: old sessions, posts, scripts, notes, drafts they killed, feedback they gave. If you can hand a repo to an agent and read markdown, this is for you.

## Why does it exist?

Because an agent that doesn't know your taste, context, and standards averages the internet. It produces competent, generic work that belongs to nobody. More prompting doesn't fix that — you can't fit your whole brain into a prompt every time, and whatever you teach it evaporates at the next session.

The fix is a brain the agent can load: who you are, how you talk, what you like, what you reject, and every correction you've ever given — stored as files, compounding over time.

## How do I use it?

Clone this repo, open it with your agent, and paste the prompt from [REPO-USE-PROMPT.md](REPO-USE-PROMPT.md). Variants exist for Claude Code, Cursor, Hermes, and any generic agent.

The short version:

```
Read README.md and AGENTS.md. Use this repo to build my Creative Brain.
First ask me where my source material is. Do not generate final content yet.
Audit my sources, interview me in small rounds, create files under outputs/<name>/,
write a creative-identity skill, run a before/after proof, then ask for feedback
and update the system.
```

The agent's first action is always the same: ask you where your source material lives. It never starts by writing content.

## What source material should I provide?

Whatever you have. More contrast is better than more volume:

- exported Claude / ChatGPT conversations
- Cursor or Hermes session logs
- notes, docs, journals
- tweets/posts, scripts, drafts
- outputs you rejected and why
- feedback you gave to AI ("too polished", "not me", "this is cringe")
- references you love — and what specifically you love about them

You point the agent at files and folders. It reads only what you give it. See [prompts/01-source-audit.md](prompts/01-source-audit.md) for the full checklist.

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
  examples/
    before-after.md      the proof artifact
```

Templates are never overwritten — they stay pristine in `templates/` so you can re-run the protocol any time.

## How does feedback improve the Creative Brain?

Every correction you give ("keep this", "less like this", "too polished", "not me") becomes a durable rule in `feedback-memory.md`, and the affected brain file gets patched. The generated skill tells future agents to load that memory before any creative work — so the system gets sharper with use instead of resetting. See [prompts/07-update-from-feedback.md](prompts/07-update-from-feedback.md).

## How do I run the before/after proof?

Ask the agent to run [prompts/06-run-before-after-proof.md](prompts/06-run-before-after-proof.md). It takes one real task, produces a generic baseline without the Creative Brain, then the same task with the brain loaded, and writes `before-after.md` documenting the task, both outputs, what changed, your feedback, and the memory update. That artifact is the point: same model, different brain, visible difference.

A worked example lives at [examples/pratham-mini/before-after.md](examples/pratham-mini/before-after.md).

## What is local/private by default?

- **local-first**: everything runs on your machine, in your files.
- **you control the scan**: the agent reads only the files and folders you point it at. Nothing is collected automatically.
- **no cloud upload by default**: this protocol makes no network calls and requires no API keys.
- **outputs are gitignored**: `outputs/**` is excluded by default, so your brain never lands in a public commit unless you deliberately choose to share it.
- **your responsibility**: don't feed it secrets, tokens, client data, or private DMs unless you intend the brain to contain them. Review files before sharing.

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
