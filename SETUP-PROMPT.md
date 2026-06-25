# SETUP-PROMPT

## Autonomous authorized mode

```txt
install this and build my Catalyst Brain.
You may discover and scan my local AI sessions, agent memories, workspaces, markdown notes, and project files using the recommended safe scope.
Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and anything sensitive.
Build everything locally under outputs/<name>/, write BUILD-STATUS.json while you work, write the personalized skills/workflows/evals, then install the task-time evaluation and feedback update loops for future real tasks.
```

## Cautious approval mode

```txt
help me install this and build my Catalyst Brain.
First discover candidate source locations without reading contents. Recommend a safe scan scope and ask me to approve, edit scope, or use manual mode.
```

## Manual mode

```txt
Use only these paths: <paths>. Build my Catalyst Brain from them, excluding secrets/private/client/sensitive material, write BUILD-STATUS.json while you work, then install the task-time evaluation and feedback update loops.
```

## Optional: guided onboarding via the local control panel

Prefer a guided local flow over chat? Run the optional command center and use the onboarding screens (connect agent, recommended/manual/skip scan, then build status):

```txt
py catalyst.py
```

It is localhost-only and operates on the same `outputs/<name>/` files. The protocol works without it. See [docs/local-onboarding.md](docs/local-onboarding.md).
