# @trycatalyst/cli

Tiny npm launcher for the local Catalyst engine.

Future ideal:

```txt
npx catalyst local
```

Working scoped command before the unscoped package exists:

```txt
npx @trycatalyst/cli local
```

Local development:

```txt
node packages/cli/bin/catalyst.mjs --help
node packages/cli/bin/catalyst.mjs local --repo C:/Users/Rakesh/Desktop/catalyst --no-open
```

The CLI checks for Python, resolves a Catalyst checkout, starts `python catalyst.py`,
prints the local URL, and leaves the server attached to the terminal. Stop it with
Ctrl+C. It does not ask for secrets and does not run commands from browser input.
