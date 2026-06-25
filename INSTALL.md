# INSTALL

Catalyst is a local engine and agent protocol. The repo has no package install required for the core protocol: clone/open the repo, then let an agent run setup.

Do not stop at clone. Cloning/opening the repo is only step one; the protocol install is complete only after setup has run and `outputs/<name>/` contains the Catalyst Brain, skills, workflows, evals, `SUMMARY.md`, `BUILD-STATUS.json`, and the installed task-time evaluation loop.

## One-command local app

Future ideal:

```txt
npx catalyst local
```

Working scoped package before the unscoped name is available:

```txt
npx @trycatalyst/cli local
```

Local development:

```txt
node packages/cli/bin/catalyst.mjs local --repo C:/Users/Rakesh/Desktop/catalyst
node packages/cli/bin/catalyst.mjs local --repo C:/Users/Rakesh/Desktop/catalyst --no-open
```

The launcher checks for Python, starts `catalyst.py`, prints `http://127.0.0.1:8765`, and keeps the server attached to the terminal. Stop server: press Ctrl+C in that terminal.

## Install means

1. receive the GitHub repo link / repo URL, then clone or open this repo
2. read `README.md`, `AGENTS.md`, and `REPO-USE-PROMPT.md`
3. optionally run verification with `python evals/run_all.py` or `py evals/run_all.py`
4. run setup: discover candidate local sources with `tools/discover_sessions.py`
5. determine authorization mode:
   - autonomous authorized mode: if the user pre-authorized the recommended scan, proceed without a second approval
   - dashboard permission mode: read `.catalyst/permissions.json` if it exists
   - cautious approval mode: ask one approval question - approve recommended scan, edit scope, or manual mode
6. read contents only inside the approved scope / authorized scope
7. build `outputs/<name>/` from templates and approved evidence
8. write `BUILD-STATUS.json` while building, then `SUMMARY.md`, skills/workflows/evals, and proposed-updates
9. install the task-time evaluation and feedback update loops for future real tasks
10. ask for feedback when the brain needs clarification or when real work is reviewed

## Permission-block handling

If content access is blocked or authorization is unclear, stop before reading file contents and ask for approval, edited scope, or manual mode. Exclusions always bind under authorization: secrets, tokens, private DMs, client data, binaries, vendor/build folders, and sensitive material stay excluded.

## Minimal user burden

The user burden should be almost no path hunting: the agent discovers candidate locations, recommends a safe scan preset, asks only for approval/feedback when needed, and then runs setup.

## Optional dashboard

Setup can run as an agent following `AGENTS.md`, or through the optional local dashboard:

```txt
py catalyst.py
py catalyst.py --no-open
```

It opens on `http://127.0.0.1:8765` as a command center:

```txt
Promise -> Connect agent -> Source permission -> Build status -> Command center
```

The dashboard is not the builder in v0. It gives Claude Code, Codex, Cursor, Hermes, and manual MCP instructions; stores `.catalyst/permissions.json`; and renders `outputs/<name>/BUILD-STATUS.json` plus the local Catalyst Brain your agent writes.

BYOK is optional (mock mode needs no key). A hosted model/provider may receive approved context only if you enable a provider or run the protocol inside a hosted agent. For multi-agent access, `py tools/mcp_server.py` runs a local-only MCP scaffold. See [docs/local-onboarding.md](docs/local-onboarding.md), [docs/control-panel.md](docs/control-panel.md), [docs/byok.md](docs/byok.md), and [docs/mcp.md](docs/mcp.md).

## Privacy

Discovery is read-only. Content scanning is authorized. Exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and sensitive material. Outputs are gitignored. The local dashboard binds localhost only and never writes to `templates/`.

If port 8765 is stuck on Windows, close the Python process that started Catalyst, or inspect it with `netstat -ano | findstr :8765` and stop only that process.

## Verify

```txt
python evals/run_all.py
py evals/run_all.py
```
