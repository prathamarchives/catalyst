# INSTALL

Read this first if someone told you to "install this repo." You are probably an agent. This page exists so you do not get this wrong.

## catalyst has nothing to install in the package-manager sense

It is a markdown-first agent protocol. There is no app, no server, no build, no dependency tree. Installing it means **cloning/opening the repo, verifying it, then running the setup protocol with your agent.** No `npm install`, no `pip install`, no `package.json`, no `requirements.txt`, no `setup.py` — their absence is expected, not a problem.

**Required understanding — do not skip:**

> There is no package install. The protocol install is complete. Next I'll run the Creative Brain setup: discover sources, recommend a scan scope, ask approval, build the brain, write the skill, and run proof.

If you cloned the repo and concluded "no package.json, so there's nothing to install" — that is the exact failure this page prevents. **Do not stop at clone.** Cloning is step one of install; setup is the rest.

## install flow

### 1. From a repo link

The user gives you a GitHub link and says some version of "install this and build my Creative Brain." The strongest version is the **one-shot autonomous prompt**, which pre-authorizes the safe scan so you don't stop to ask a second time:

```txt
https://github.com/prathamarchives/catalyst
install this and build my Creative Brain.
You may discover and scan my local AI sessions, agent memories, workspaces, markdown notes, and project files using the recommended safe scope.
Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and anything sensitive.
Build everything locally, write the personalized skill/workflows/evals, run a before/after proof, then ask me for taste feedback and update the brain.
```

That prompt unlocks **autonomous authorized mode** (see step 5). If the user only said "install this," you're in **cautious approval mode** and ask one approval question before reading. Either way, clone it:

```
git clone https://github.com/prathamarchives/catalyst
```

Or, if the repo is already open in your workspace, just open it. Either way you now have the files locally.

### 2. Recognize what it is

This is a **protocol repo**, not an application. The product is the markdown: `AGENTS.md` is the operating protocol, `prompts/` is the step-by-step, `templates/` are the blueprints, `tools/discover_sessions.py` is a read-only discovery helper. See [docs/install-vs-use.md](docs/install-vs-use.md).

### 3. No dependencies

Nothing to install. The only executable code is the eval harness and the discovery helper, both **Python standard library only** — no third-party packages.

### 4. Optional: verify the repo

You may confirm the repo is intact by running the eval harness:

```
py evals/run_all.py        # Windows launcher
python evals/run_all.py    # if python is on PATH
```

Exit code `0` and `RESULT: ALL PASS` means the protocol is intact. This is **optional verification**, not a required install step — skipping it does not block setup.

**If eval execution is blocked** (a permission classifier may refuse to run code from a freshly cloned external repo): that is a reasonable guardrail, not a failure. Say so, tell the user they can run `py evals/run_all.py` themselves if they want the check, and **continue to setup anyway** — verification is optional and never gates the build. Do not treat a blocked eval as "install failed."

### 5. Install is complete — now run setup

Once the repo is cloned/opened, **the protocol install is complete.** Do not stop here and do not ask "want me to do anything else?" Proceed directly into setup. Say, in substance:

> There is no package install. This is a protocol repo, so install is complete. Next I'll run setup: discover sources, recommend a scan scope, ask approval, build the brain, write the skill, and run proof.

Then run [prompts/08-install-and-run.md](prompts/08-install-and-run.md), which is the full operating procedure.

## setup, in one paragraph

Discover where the user's AI sessions, exports, notes, and workspaces live (run `tools/discover_sessions.py` — read-only, paths only). Recommend a **safe scan scope** instead of dumping a folder list. Ask **one** approval question — approve recommended scan / edit scope / manual mode — not a path-management quiz. Scan only the approved scope. Inventory before deep reading; prioritize rejected outputs and feedback. Build the brain under `outputs/<name>/creative-brain/`, write the customized skill, copy the workflows, initialize the blind A/B log, run the before/after proof (and a blind A/B proof when possible), ask for feedback, and fold it into `feedback-memory.md` and the skill. Then set a memory-distillation cadence and hand off.

## autonomous authorized mode vs. cautious approval mode

Two modes, decided by the user's opening instruction:

- **Autonomous authorized mode (Mode A).** The prompt already authorized discovery + the recommended safe scan (excluding secrets/client/DMs/sensitive). **Do not ask the approval question again.** Announce the scope in one line and proceed.
- **Cautious approval mode (Mode B).** Authorization is ambiguous ("install this"). Discover first, then ask exactly **one** approval question before reading contents.

Do not make the user manage filesystem paths in either mode. The Mode B question has exactly this shape:

> I recommend scanning AI sessions, exports, and markdown-heavy workspaces while excluding secrets/client/private-DM/vendor/build/binary folders. Approve recommended scan, edit scope, or manual mode?

Whichever mode: read only inside the authorized scope, and the exclusions always bind.

## where outputs go

Everything the agent builds lands under `outputs/<your-name-or-project>/`:

```
outputs/<name>/
  creative-brain/   (ten files)
  skills/catalyst-skill.md
  workflows/        (five workflows, copied + customized)
  evals/blind-ab-log.md
  examples/before-after.md
  README.md
```

`outputs/**` is gitignored by default — your brain never lands in a public commit unless you choose to share it.

## privacy / model-provider caveat

This protocol makes no network calls and needs no API keys. Discovery checks that paths exist; it reads nothing until you approve a scope. **Caveat:** the agent/model you run this with may send approved context to its provider. The repo can't control that — check your tool's privacy policy before approving sensitive material. Full model: [docs/permission-model.md](docs/permission-model.md) and [docs/privacy.md](docs/privacy.md).

## troubleshooting

- **"There's no package.json / requirements.txt — is it broken?"** No. It's a protocol repo; their absence is expected. Install = clone + verify + run setup.
- **"The eval command was blocked."** Optional verification only. Tell the user they can run it themselves; continue to setup.
- **"Discovery found nothing."** Fall back to manual mode: ask the user to point you at their exports/notes/drafts directly. See [prompts/01-source-audit.md](prompts/01-source-audit.md).
- **"`python` isn't recognized" (Windows).** Use the `py` launcher: `py evals/run_all.py`.
- **"The agent stopped after cloning."** That's the known failure mode. Reopen this file and continue from step 5.
