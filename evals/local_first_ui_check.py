"""Eval: the optional control panel + BYOK stay local-first, consent-safe, and
keyless-by-default. Protects the hard rules even as the UI evolves.

Checks:
- .env.example exists and contains NO real key value
- no hardcoded API key anywhere under apps/
- the control panel binds localhost by default and exposes no shell/exec endpoint
- file writes are confined to outputs/ (never templates/)
- a mock provider exists and is the no-key fallback
- README states the core works with no account / no database / no required key /
  optional UI / optional BYOK
- .gitignore ignores .env and .catalyst/
"""
import re
from pathlib import Path

KEY_VARS = ["OPENROUTER_API_KEY", "CATALYST_API_KEY"]
SECRET_RE = re.compile(r"sk-[A-Za-z0-9][A-Za-z0-9_-]{12,}")


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def run(root: Path) -> list:
    failures = []
    apps = root / "apps"

    # If no app layer exists yet, only the doc/positioning rules apply.
    has_app = apps.is_dir()

    # --- .env.example ---
    env_example = root / ".env.example"
    if not env_example.is_file():
        failures.append(".env.example is missing")
    else:
        text = _read(env_example)
        if not any(v in text for v in KEY_VARS):
            failures.append(".env.example does not declare a provider key var")
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() in KEY_VARS and value.strip():
                failures.append(f".env.example must not contain a real key value for {name.strip()}")
        if SECRET_RE.search(text):
            failures.append(".env.example contains something that looks like a real secret")

    # --- no hardcoded keys under apps/ (authored source only) ---
    if has_app:
        skip_dirs = {"node_modules", "dist"}  # third-party + build artifacts, not authored code
        for f in apps.rglob("*"):
            if skip_dirs & set(f.parts):
                continue
            if not f.is_file() or f.suffix not in {".py", ".js", ".ts", ".tsx", ".json", ".html"}:
                continue
            body = _read(f)
            if SECRET_RE.search(body):
                failures.append(f"possible hardcoded secret in {f.relative_to(root).as_posix()}")
            for v in KEY_VARS:
                # assignment of a literal key value (not os.environ access) is banned
                if re.search(rf"{v}\s*=\s*[\"'][^\"']+[\"']", body):
                    failures.append(f"hardcoded {v} literal in {f.relative_to(root).as_posix()}")

    # --- server safety ---
    server = apps / "control-panel" / "server.py"
    if has_app and server.is_file():
        s = _read(server)
        if "127.0.0.1" not in s:
            failures.append("server.py does not bind 127.0.0.1 by default")
        for danger in ["os.system(", "subprocess.", "shell=True", "eval(input", "exec(input"]:
            if danger in s:
                failures.append(f"server.py exposes a dangerous call: {danger}")
        if "WRITE_ROOTS" not in s or '"outputs"' not in s:
            failures.append("server.py does not declare an outputs-only write allowlist")
        if "templates" in s and 'WRITE_ROOTS = ["outputs"]' not in s:
            # ensure templates is not in the write set
            if re.search(r"WRITE_ROOTS\s*=\s*\[[^\]]*templates", s):
                failures.append("server.py allows writes to templates/")

    # --- mock provider / keyless fallback ---
    byok = apps / "control-panel" / "byok.py"
    if has_app and byok.is_file():
        b = _read(byok)
        if "class MockProvider" not in b:
            failures.append("byok.py has no MockProvider")
        if "def get_provider" not in b:
            failures.append("byok.py has no get_provider()")
        if "MockProvider()" not in b:
            failures.append("byok.py does not fall back to MockProvider")

    # --- README local-first promises ---
    readme = _read(root / "README.md").lower()
    for need in ["no account", "no database", "optional"]:
        if need not in readme:
            failures.append(f"README missing local-first promise: '{need}'")
    if not any(m in readme for m in ["no api key", "no required api key", "with no api key", "with no\xa0api key"]):
        failures.append("README does not state the core works with no API key")
    if "byok is optional" not in readme:
        failures.append("README does not state BYOK is optional")

    # --- no browser-stored keys ---
    static = root / "apps" / "control-panel" / "static"
    if static.is_dir():
        for f in static.glob("*.js"):
            js = _read(f).lower()
            if "localstorage" in js or "sessionstorage" in js:
                failures.append(f"{f.relative_to(root).as_posix()} uses browser storage (no keys may be stored client-side)")

    # --- MCP scaffold safety ---
    mcp = root / "tools" / "mcp_server.py"
    if mcp.is_file():
        m = _read(mcp)
        for danger in ["os.system(", "subprocess.", "shell=True", "urllib.request", "socket.", "requests."]:
            if danger in m:
                failures.append(f"mcp_server.py exposes network/shell: {danger}")
        if "outputs" not in m:
            failures.append("mcp_server.py does not confine writes to outputs/")

    # --- gitignore ---
    gi = _read(root / ".gitignore")
    for need in [".env", ".catalyst/"]:
        if need not in gi:
            failures.append(f".gitignore missing: {need}")

    return failures


if __name__ == "__main__":
    import sys
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL local_first_ui_check:", p)
    if not problems:
        print("PASS local_first_ui_check")
    sys.exit(1 if problems else 0)
