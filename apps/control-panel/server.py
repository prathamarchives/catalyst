"""server.py — Catalyst local control panel (optional).

A zero-dependency, local-first control surface for the Catalyst Brain. It is a
control panel for the living local files, NOT the product. The product is the
markdown protocol in AGENTS.md; this server only makes it easier to see and
operate. Catalyst works fully without ever running this.

Run:
    py apps/control-panel/server.py
    python apps/control-panel/server.py
Then open http://127.0.0.1:8765

Design choice (documented in apps/control-panel/README.md): this is Python
stdlib + a vanilla HTML/CSS/JS single page, not a Next.js app. Reason: the repo
is deliberately dependency-free (no npm, no node_modules, no build step). A
heavy web stack would contradict the "lighter and deeper, optional control
panel" positioning. The HTTP API here is the documented "bridge".

Security model:
- binds 127.0.0.1 by default (override with CATALYST_HOST / CATALYST_PORT)
- if bound to a non-local host, a bearer token (CATALYST_TOKEN) is REQUIRED
- NO shell/exec endpoint of any kind
- NO arbitrary filesystem access: every path is resolved and must stay inside an
  allowlisted repo-relative root
- writes are restricted to outputs/ (the generated brain) and the local-only
  .catalyst/ config dir; templates/ are never written (protocol: never overwrite
  templates)
- reads are restricted to outputs/, templates/, docs/, prompts/
- the BYOK key is never returned to the browser
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
STATIC_DIR = HERE / "static"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "tools"))
import byok  # noqa: E402

try:
    import discover_sessions  # noqa: E402
except Exception:  # pragma: no cover
    discover_sessions = None

# --- allowlist ---------------------------------------------------------------
READ_ROOTS = ["outputs", "templates", "docs", "prompts"]
WRITE_ROOTS = ["outputs"]  # never templates/
BRAIN_FILE_ORDER = [
    "README.md", "identity.md", "context.md", "goals.md", "constraints.md",
    "standards.md", "judgment.md", "taste.md", "voice.md", "anti-slop.md",
    "references.md", "rejected-examples.md", "decision-rules.md",
    "task-patterns.md", "feedback-memory.md", "lexicon.md", "open-questions.md",
]

HOST = os.environ.get("CATALYST_HOST", "127.0.0.1")
PORT = int(os.environ.get("CATALYST_PORT", "8765"))
TOKEN = os.environ.get("CATALYST_TOKEN", "")
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _safe_path(rel: str, roots) -> Path | None:
    """Resolve rel under REPO_ROOT and ensure it stays inside an allowlisted root."""
    if rel is None:
        return None
    rel = rel.replace("\\", "/").lstrip("/")
    if ".." in rel.split("/"):
        return None
    candidate = (REPO_ROOT / rel).resolve()
    for root in roots:
        base = (REPO_ROOT / root).resolve()
        try:
            candidate.relative_to(base)
            return candidate
        except ValueError:
            continue
    return None


def _slug(name: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in (name or "").strip()]
    s = "".join(keep)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-") or "me"


def _list_brains() -> list:
    out_dir = REPO_ROOT / "outputs"
    brains = []
    if not out_dir.is_dir():
        return brains
    for child in sorted(out_dir.iterdir()):
        if child.name == ".gitkeep" or not child.is_dir():
            continue
        brain_dir = child / "catalyst-brain"
        present = []
        missing = []
        for f in BRAIN_FILE_ORDER:
            (present if (brain_dir / f).is_file() else missing).append(f)
        proof = child / "evals" / "improvement-log.md"
        brains.append({
            "name": child.name,
            "path": str(child),
            "brain_present": (present if brain_dir.is_dir() else []),
            "brain_missing": (missing if brain_dir.is_dir() else BRAIN_FILE_ORDER),
            "has_skills": (child / "skills").is_dir(),
            "has_workflows": (child / "workflows").is_dir(),
            "has_evals": (child / "evals").is_dir(),
            "last_proof_log": str(proof) if proof.is_file() else None,
        })
    return brains


def _parse_brain_meta(text: str) -> dict:
    """Pull the protocol section headers out of a brain file for the explorer."""
    meta = {}
    current = None
    buf = []
    wanted = {"purpose", "when to load", "tasks affected", "how to apply",
              "how to update", "what not to put here"}
    for line in text.splitlines():
        if line.startswith("## "):
            if current in wanted:
                meta[current] = "\n".join(buf).strip()
            head = line[3:].strip().lower()
            current = head if head in wanted else None
            buf = []
        elif current in wanted:
            buf.append(line)
    if current in wanted:
        meta[current] = "\n".join(buf).strip()
    return meta


def _scaffold_brain(name: str, answers: dict) -> dict:
    """Copy templates into outputs/<slug>/ and seed with onboarding answers.

    No scanning happens here. This is the no-key, consent-free path: it only
    writes the user's own typed answers into their own local brain.
    """
    slug = _slug(name)
    dest = REPO_ROOT / "outputs" / slug
    for sub in ["catalyst-brain", "skills", "workflows", "evals"]:
        src = REPO_ROOT / "templates" / sub
        if src.is_dir():
            shutil.copytree(src, dest / sub, dirs_exist_ok=True)
    # top-level README for the generated brain
    (dest / "README.md").write_text(
        f"# {name} — Catalyst Brain\n\n"
        "Generated locally by the Catalyst control panel onboarding. This is a\n"
        "seeded brain from your typed answers. Point an agent at it (see the\n"
        "Export tab) to run discovery, scan approved sources, and deepen it.\n",
        encoding="utf-8",
    )
    # capture raw answers verbatim for evidence
    lines = [f"# onboarding answers — {name}", ""]
    for k, v in answers.items():
        lines.append(f"## {k}")
        lines.append("")
        lines.append((v or "").strip() or "(left blank)")
        lines.append("")
    (dest / "onboarding-answers.md").write_text("\n".join(lines), encoding="utf-8")

    # seed specific brain files with the answers as observed evidence
    seed_map = {
        "identity.md": answers.get("name"),
        "goals.md": answers.get("using_for"),
        "constraints.md": answers.get("never_ship"),
        "taste.md": answers.get("approved_examples"),
        "rejected-examples.md": answers.get("rejected_examples"),
        "task-patterns.md": answers.get("first_task"),
    }
    brain = dest / "catalyst-brain"
    for fname, value in seed_map.items():
        if not value:
            continue
        p = brain / fname
        if not p.is_file():
            continue
        block = (
            "\n\n## seeded from onboarding\n\n"
            "- status: observed\n"
            "  evidence: user typed this during control-panel onboarding\n"
            f"  rule: {value.strip()}\n"
        )
        p.write_text(p.read_text(encoding="utf-8") + block, encoding="utf-8")
    return {"name": name, "slug": slug, "path": str(dest)}


# --- HTTP handler ------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "Catalyst/0.2"

    def log_message(self, *a):  # quieter console
        pass

    # -- helpers --
    def _auth_ok(self) -> bool:
        if self.client_address[0] in LOCAL_HOSTS and HOST in LOCAL_HOSTS:
            return True
        if not TOKEN:
            return False
        return self.headers.get("Authorization", "") == f"Bearer {TOKEN}"

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200):
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except ValueError:
            return {}

    # -- routing --
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/"):
            if not self._auth_ok():
                return self._json({"error": "unauthorized (non-local host requires CATALYST_TOKEN)"}, 401)
            return self._api_get(path, parse_qs(parsed.query))
        return self._serve_static(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            return self._json({"error": "not found"}, 404)
        if not self._auth_ok():
            return self._json({"error": "unauthorized"}, 401)
        return self._api_post(parsed.path, self._read_json())

    # -- static --
    def _serve_static(self, path: str):
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        target = (STATIC_DIR / rel).resolve()
        try:
            target.relative_to(STATIC_DIR)
        except ValueError:
            return self._send(403, b"forbidden", "text/plain")
        if not target.is_file():
            return self._send(404, b"not found", "text/plain")
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".svg": "image/svg+xml",
        }.get(target.suffix, "application/octet-stream")
        self._send(200, target.read_bytes(), ctype)

    # -- GET api --
    def _api_get(self, path: str, q: dict):
        if path == "/api/status":
            cfg = byok.get_config()
            return self._json({
                "repo_root": str(REPO_ROOT),
                "brains": _list_brains(),
                "byok": {
                    "effective_provider": cfg["effective_provider"],
                    "mock_mode": cfg["mock_mode"],
                    "has_key": cfg["has_key"],
                    "model": cfg["model"],
                },
                "brain_file_order": BRAIN_FILE_ORDER,
            })
        if path == "/api/discover":
            if discover_sessions is None:
                return self._json({"found": [], "missing_categories": [], "note": "discovery helper unavailable"})
            res = discover_sessions.discover()
            # collapse to category counts so we never dump giant path lists
            cats = {}
            for item in res.get("found", []):
                cats.setdefault(item["category"], 0)
                cats[item["category"]] += 1
            return self._json({
                "categories": [{"category": c, "count": n} for c, n in sorted(cats.items())],
                "missing_categories": res.get("missing_categories", []),
                "note": "read-only path discovery. nothing was read. you approve any scan.",
            })
        if path == "/api/brain":
            name = (q.get("name") or [""])[0]
            brain = (REPO_ROOT / "outputs" / name / "catalyst-brain")
            if not _safe_path(f"outputs/{name}/catalyst-brain", READ_ROOTS) or not brain.is_dir():
                return self._json({"error": "brain not found"}, 404)
            files = []
            for f in BRAIN_FILE_ORDER:
                p = brain / f
                if not p.is_file():
                    continue
                meta = _parse_brain_meta(p.read_text(encoding="utf-8"))
                files.append({"file": f, "meta": meta})
            return self._json({"name": name, "files": files})
        if path == "/api/file":
            name = (q.get("name") or [""])[0]
            rel = (q.get("path") or [""])[0]
            full = _safe_path(f"outputs/{name}/{rel}", READ_ROOTS)
            if not full or not full.is_file() or full.suffix != ".md":
                return self._json({"error": "file not allowed or not found"}, 404)
            return self._json({"path": rel, "content": full.read_text(encoding="utf-8")})
        if path == "/api/template":
            rel = (q.get("path") or [""])[0]
            full = _safe_path(f"templates/{rel}", READ_ROOTS)
            if not full or not full.is_file():
                return self._json({"error": "not found"}, 404)
            return self._json({"path": rel, "content": full.read_text(encoding="utf-8")})
        if path == "/api/export":
            brains = _list_brains()
            name = brains[0]["name"] if brains else "<name>"
            prompt = (
                "Read README.md and AGENTS.md in this repo. Use my existing Catalyst Brain at "
                f"outputs/{name}/catalyst-brain/. Load the relevant files before the task, "
                "produce the work, review it against my standards/judgment/rejected-examples, "
                "show me, capture my feedback, and update the brain."
            )
            return self._json({
                "brain_path": f"outputs/{name}/catalyst-brain/",
                "agent_prompt": prompt,
                "no_ui_note": "You never need this control panel. Point any agent at AGENTS.md and the brain path above.",
            })
        return self._json({"error": "unknown endpoint"}, 404)

    # -- POST api --
    def _api_post(self, path: str, data: dict):
        if path == "/api/file":
            name = data.get("name", "")
            rel = data.get("path", "")
            content = data.get("content", "")
            full = _safe_path(f"outputs/{name}/{rel}", WRITE_ROOTS)
            if not full or full.suffix != ".md":
                return self._json({"error": "write not allowed (outputs/*.md only)"}, 403)
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
            return self._json({"ok": True, "path": rel})
        if path == "/api/onboarding":
            name = (data.get("answers", {}) or {}).get("name") or data.get("name") or ""
            if not name.strip():
                return self._json({"error": "name is required"}, 400)
            result = _scaffold_brain(name, data.get("answers", {}) or {})
            return self._json({"ok": True, **result, "brains": _list_brains()})
        if path == "/api/byok/test":
            provider = byok.get_provider()
            out = provider.complete(
                "You are validating a BYOK connection for Catalyst.",
                "Reply with one short sentence confirming the connection works.",
            )
            return self._json(out)
        if path == "/api/synthesize":
            # optional AI-assisted helper; works in mock mode with no key
            section = data.get("section", "brain section")
            material = data.get("material", "")
            provider = byok.get_provider()
            out = provider.complete(
                "You synthesize a user's raw answers into a concise Catalyst Brain "
                f"section: {section}. Keep it specific, no slop, no overclaiming.",
                material,
            )
            return self._json(out)
        return self._json({"error": "unknown endpoint"}, 404)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if HOST not in LOCAL_HOSTS and not TOKEN:
        print("REFUSING to bind a non-local host without CATALYST_TOKEN set.", file=sys.stderr)
        print("Set CATALYST_TOKEN=... or use the default 127.0.0.1.", file=sys.stderr)
        return 2
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Catalyst control panel -> http://{HOST}:{PORT}")
    print(f"repo: {REPO_ROOT}")
    cfg = byok.get_config()
    print(f"BYOK: {cfg['effective_provider']} (mock_mode={cfg['mock_mode']}). Core works with no key.")
    print("Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
