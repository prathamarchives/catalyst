"""byok.py — bring-your-own-key provider abstraction for Catalyst (optional).

BYOK is OPTIONAL. Catalyst's core — building, reading, and editing the local
Catalyst Brain, running the control panel, and exporting agent prompts — works
with no key at all. BYOK only powers optional AI-assisted helpers (synthesizing
onboarding answers, scoring brain gaps, running a standards review on an output).

Privacy: the MockProvider sends nothing anywhere. A real provider (e.g.
OpenRouter) sends the approved text you pass it to that provider's API over the
network. Enabling BYOK is the one place Catalyst can make a network call, and it
only happens when you set a key AND trigger an assisted action.

Key handling:
- the API key is read from an environment variable only (never written to a
  committed file, never returned to the browser, never logged)
- provider/model preferences may live in a local-only, gitignored config at
  `.catalyst/config.json`; the key never goes there
- if no key is set, get_provider() returns the MockProvider so the UI still works

Python standard library only.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_CONFIG = REPO_ROOT / ".catalyst" / "config.json"

# Environment variables checked for an API key, in priority order.
KEY_ENV_VARS = ["OPENROUTER_API_KEY", "CATALYST_API_KEY"]

DEFAULTS = {
    "provider": "mock",
    "model": "openrouter/auto",
    "base_url": "https://openrouter.ai/api/v1/chat/completions",
}


def _read_local_config() -> dict:
    """Read non-secret provider/model prefs from the gitignored local config."""
    if not LOCAL_CONFIG.is_file():
        return {}
    try:
        data = json.loads(LOCAL_CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    # never accept a key from the config file; keys live in env only
    data.pop("api_key", None)
    data.pop("key", None)
    return data if isinstance(data, dict) else {}


def _api_key() -> str | None:
    for var in KEY_ENV_VARS:
        val = os.environ.get(var)
        if val and val.strip():
            return val.strip()
    return None


def get_config() -> dict:
    """Resolve effective config WITHOUT exposing the key value."""
    cfg = dict(DEFAULTS)
    cfg.update(_read_local_config())
    # env overrides for provider/model if present
    cfg["provider"] = os.environ.get("CATALYST_PROVIDER", cfg["provider"])
    cfg["model"] = os.environ.get("CATALYST_MODEL", cfg["model"])
    has_key = _api_key() is not None
    cfg["has_key"] = has_key
    # mock unless a key is present AND a real provider is selected
    effective = cfg["provider"]
    if effective != "mock" and not has_key:
        effective = "mock"
    cfg["effective_provider"] = effective
    cfg["mock_mode"] = effective == "mock"
    # never leak the key
    cfg.pop("api_key", None)
    return cfg


class MockProvider:
    """Always-works, no-network provider. Deterministic, dependency-free.

    It does not synthesize anything intelligent; it formats the input so the
    judgment loop is visible and the UI is usable with no key. It is honest
    about being a placeholder.
    """

    name = "mock"

    def complete(self, system: str, user: str) -> dict:
        preview = user.strip()
        if len(preview) > 600:
            preview = preview[:600] + " …"
        text = (
            "[mock provider — no API key set, nothing was sent over the network]\n\n"
            "This is a deterministic placeholder so the loop is visible without BYOK.\n"
            "Set an API key (see .env.example) to get real AI-assisted synthesis.\n\n"
            "--- input the assisted action would have sent ---\n"
            f"{preview}"
        )
        return {"text": text, "provider": "mock", "sent_over_network": False}


class OpenRouterProvider:
    """Minimal OpenRouter chat-completions client over urllib (no deps)."""

    name = "openrouter"

    def __init__(self, key: str, model: str, base_url: str):
        self._key = key
        self.model = model
        self.base_url = base_url

    def complete(self, system: str, user: str) -> dict:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            self.base_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self._key}",
                "Content-Type": "application/json",
                "X-Title": "Catalyst Control Panel",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            return {"text": "", "provider": "openrouter", "error": f"HTTP {exc.code}: {detail}", "sent_over_network": True}
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            return {"text": "", "provider": "openrouter", "error": str(exc), "sent_over_network": True}
        text = (
            body.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        return {"text": text, "provider": "openrouter", "model": self.model, "sent_over_network": True}


def get_provider():
    """Return a provider instance. MockProvider unless a real key+provider exist."""
    cfg = get_config()
    if cfg["mock_mode"]:
        return MockProvider()
    key = _api_key()
    if not key:
        return MockProvider()
    return OpenRouterProvider(key=key, model=cfg["model"], base_url=cfg["base_url"])


if __name__ == "__main__":
    c = get_config()
    print("provider:", c["effective_provider"], "| mock_mode:", c["mock_mode"], "| has_key:", c["has_key"])
    p = get_provider()
    out = p.complete("You are a test.", "Say hello.")
    print("sent_over_network:", out.get("sent_over_network"))
    print(out["text"][:200])
