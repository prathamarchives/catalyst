# SETUP-PROMPT

## Autonomous authorized mode

```txt
install this and build my Catalyst Brain.
You may discover and scan my local AI sessions, agent memories, workspaces, markdown notes, and project files using the recommended safe scope.
Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and anything sensitive.
Build everything locally under outputs/<name>/, write the personalized skills/workflows/evals, run the first real task through task-time evaluation, then ask me for feedback and update the brain.
```

## Cautious approval mode

```txt
help me install this and build my Catalyst Brain.
First discover candidate source locations without reading contents. Recommend a safe scan scope and ask me to approve, edit scope, or use manual mode.
```

## Manual mode

```txt
Use only these paths: <paths>. Build my Catalyst Brain from them, excluding secrets/private/client/sensitive material, then install the task-time evaluation and feedback update loops.
```

## Optional: guided onboarding via the local control panel

Prefer a guided local flow over chat? Run the optional control panel and use the Onboarding screen (5–7 questions, recommended/manual/skip scan, then a proof task):

```txt
py apps/control-panel/server.py
```

It is localhost-only and operates on the same `outputs/<name>/` files. The protocol works without it. See [docs/local-onboarding.md](docs/local-onboarding.md).
