# BYOK — bring your own key (optional)

BYOK is optional and off by default. Catalyst's core never needs it.

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
