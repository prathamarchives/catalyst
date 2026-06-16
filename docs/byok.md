# BYOK — bring your own key (optional)

BYOK is optional and off by default. Catalyst's core never needs it. But note the
honest trade-off: Catalyst's *real value* — synthesis, evaluation, and updates —
needs a connected AI/agent. With no connection you get templates and a deterministic
mock, not judgment. BYOK (or the manual-prompt path) is how you connect one.

## Connection modes

The control panel's first step is **Connect AI**, offered honestly by status:

- **Mock / offline** — always available, no network, deterministic placeholder. Demo only; not live AI.
- **OpenRouter BYOK** — real synthesis/evaluation on approved text. Key from env only.
- **Claude Code / Codex / Hermes CLI** — detected via `shutil.which` (existence only — login state unknown; v0.3 detects, it does not run the CLI for you).
- **Manual LLM prompt** — always available; copy a prompt into any LLM and paste the result back. The best no-key path to real synthesis.

CLI detection never executes anything from user input. The UI must not present mock as if it were a live model.

## Works with no key

These never require a key and never make a network call:

- reading and editing the Catalyst Brain
- running the local control panel
- read-only source discovery
- exporting prompts for an agent
- using Catalyst manually with any agent (Claude Code, Hermes, Cursor, Codex)

With no key set, the panel and helper module use a **mock provider**: deterministic, dependency-free, and explicit that nothing was sent anywhere.

## What a key adds

A key powers optional AI-assisted helpers:

- synthesize onboarding answers into initial brain sections
- summarize approved sources
- score gaps in brain quality
- suggest updates after feedback
- run a standards/judgment review on a task output

## How to enable

```txt
cp .env.example .env
# edit .env:
#   OPENROUTER_API_KEY=sk-or-...
# optional:
#   CATALYST_PROVIDER=openrouter
#   CATALYST_MODEL=openrouter/auto
py apps/control-panel/server.py
```

OpenRouter is the first supported provider. The provider abstraction lives in `apps/control-panel/byok.py`; adding another provider is a small class with a `complete()` method.

## Privacy

- the key is read from an **environment variable only** — never typed into the web page, never returned to the browser, never logged, never committed
- non-secret preferences (provider, model) may live in a local-only, gitignored `.catalyst/config.json`; the key never goes there
- `.env` and `.catalyst/` are gitignored
- enabling BYOK is the **one** place Catalyst makes a network call. When you trigger an assisted action, only the text you pass to it (onboarding answers, a draft you submit for review) is sent to your chosen provider. Nothing is sent in mock mode.
- do not approve sensitive material into a brain you then send through a hosted provider unless you accept that provider's privacy terms

## Mock-mode guarantee

If `OPENROUTER_API_KEY` (or `CATALYST_API_KEY`) is unset, `get_provider()` returns the mock provider regardless of other settings. The UI degrades cleanly: every screen still works, and assisted output is clearly labeled as mock.
