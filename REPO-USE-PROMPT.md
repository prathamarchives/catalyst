# REPO-USE-PROMPT — copy/paste this to your agent

## Install from a link

Autonomous authorized mode:

```txt
https://github.com/prathamarchives/catalyst
install this and build my Catalyst Brain.
You may discover and scan my local AI sessions, agent memories, workspaces, markdown notes, and project files using the recommended safe scope.
Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and anything sensitive.
Build everything locally, write the personalized skills/workflows/evals, run the first real task through the task-time evaluation loop, then ask me for feedback and update the brain.
```

Cautious approval mode:

```txt
https://github.com/prathamarchives/catalyst
help me install this and build my Catalyst Brain
```

This is a protocol repo, not an app. A correct agent does not stop at clone and must never overwrite templates. It discovers candidate sources, gates reading on authorization, audits approved material, interviews in small rounds, builds `outputs/<name>/`, writes skills/evals/workflows, and installs the feedback loop. See [INSTALL.md](INSTALL.md).

## Core prompt inside the repo

```txt
Read README.md and AGENTS.md. Use this repo to build my Catalyst Brain.
First discover where my AI sessions, notes, exports, agent memories, and workspaces live. Do not read file contents yet.
Show me the discovered locations, recommend a safe scan scope, ask what you may scan if I did not already authorize it, then audit only the approved scope.
Interview me in small rounds, extract identity/context/standards/judgment/taste/feedback with evidence, create files under outputs/<name>/, write Catalyst skills/workflows/evals, run a real task through task-time evaluation, then ask for feedback and update the system so it compounds session to session.
```

## What to expect

1. The agent discovers candidate source locations.
2. You approve scan scope unless already authorized.
3. It audits and interviews.
4. It builds a Catalyst Brain and skill package.
5. It uses the brain on a real task, reviews against your standards, captures feedback, and updates the system.

If the agent starts producing final work before building the brain and standards loop, stop it and point it back to AGENTS.md.

## Optional local control panel

You never need a UI — the prompts above are enough. If you want a local control surface for the brain, run `py apps/control-panel/server.py` (localhost-only, zero dependencies) and open `http://127.0.0.1:8765`. It operates on the same `outputs/<name>/` markdown and includes an Export tab that hands the brain back to any agent without the UI. BYOK is optional; mock mode needs no key. See [docs/control-panel.md](docs/control-panel.md).
