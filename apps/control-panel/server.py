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
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
STATIC_DIR = HERE / "static"
DIST_DIR = REPO_ROOT / "apps" / "web" / "dist"  # prebuilt consumer UI (Phase 3)
CATALYST_DIR = REPO_ROOT / ".catalyst"
PERMISSIONS_FILE = CATALYST_DIR / "permissions.json"
AGENT_STATUS_FILE = CATALYST_DIR / "agent-status.json"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "tools"))
import byok  # noqa: E402

try:
    import discover_sessions  # noqa: E402
except Exception:  # pragma: no cover
    discover_sessions = None

sys.path.insert(0, str(REPO_ROOT))
from catalyst_core import (  # noqa: E402
    brain_manager,
    context_assembler,
    router as flow_router,
    packet as flow_packet,
    evaluator as flow_evaluator,
    feedback_processor,
    feedback as flow_feedback,
    quality as flow_quality,
    capture as runtime_capture,
    events as runtime_events,
    graph as runtime_graph,
    health as runtime_health,
    judgment as runtime_judgment,
    memory as runtime_memory,
    proposal_engine,
    recall as runtime_recall,
    signals as runtime_signals,
    structured_evaluator,
    versioning,
)

# --- allowlist ---------------------------------------------------------------
READ_ROOTS = ["outputs", "templates", "docs", "prompts"]
WRITE_ROOTS = ["outputs"]  # never templates/
BRAIN_FILE_ORDER = [
    "README.md", "identity.md", "context.md", "goals.md", "constraints.md",
    "standards.md", "judgment.md", "taste.md", "voice.md", "anti-slop.md",
    "references.md", "rejected-examples.md", "decision-rules.md",
    "task-patterns.md", "feedback-memory.md", "lexicon.md", "open-questions.md",
]

# Brain explorer grouping: section label -> ordered files + human meaning.
BRAIN_GROUPS = [
    ("Identity / context", ["identity.md", "context.md", "goals.md", "constraints.md"]),
    ("Taste / judgment", ["standards.md", "judgment.md", "taste.md", "anti-slop.md", "rejected-examples.md"]),
    ("Operating logic", ["decision-rules.md", "task-patterns.md", "voice.md", "lexicon.md", "references.md"]),
    ("Learning", ["feedback-memory.md", "open-questions.md"]),
]

# CLI binaries we may *detect* (existence only, never executed from user input).
AGENT_CLIS = [
    ("claude-code", "Claude Code", "claude", "Install Claude Code and run `claude` once to log in."),
    ("codex", "Codex", "codex", "Install Codex and authenticate it."),
    ("cursor", "Cursor", "cursor", "Install Cursor and make `cursor` available on PATH, or use the MCP JSON fallback."),
    ("hermes", "Hermes", "hermes", "Install or point to your Hermes CLI on PATH."),
]

# A copyable prompt the user can paste into ANY LLM to produce a context packet.
EXTRACTION_PROMPT = """You are building a context packet for Catalyst, a local judgment layer for AI agents.
Analyze the person / project / workspace / context I give you and extract what an agent
would need to represent me, judge work to my standard, and improve from my corrections.

Output structured markdown with EXACTLY these sections (leave a section empty if unknown,
never invent facts):

identity:
goals:
projects:
constraints:
standards:
judgment rules:
approved examples:
rejected examples:
voice/taste:
workflows:
recurring corrections:
open questions:
sources/evidence:

Rules: be specific and concrete, prefer evidence/quotes over adjectives, mark uncertain
items as "assumed", and never include secrets, tokens, private DMs, or client data.

Context to analyze:
<paste your context here>
"""

HOST = os.environ.get("CATALYST_HOST", "127.0.0.1")
PORT = int(os.environ.get("CATALYST_PORT", "8765"))
TOKEN = os.environ.get("CATALYST_TOKEN", "")
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
PERMISSION_MODES = {"recommended", "manual", "skip"}
BUILD_STEPS = [
    {"id": "connect_agent", "label": "Connect agent", "state": "pending"},
    {"id": "discover_sources", "label": "Discover sources", "state": "pending"},
    {"id": "approve_scope", "label": "Approve scan scope", "state": "pending"},
    {"id": "extract_identity_context", "label": "Extract identity/context", "state": "pending"},
    {"id": "extract_taste_judgment", "label": "Extract taste/judgment", "state": "pending"},
    {"id": "write_brain", "label": "Write Catalyst Brain", "state": "pending"},
    {"id": "write_skills", "label": "Write skills/workflows/evals", "state": "pending"},
    {"id": "ready", "label": "Ready for agents", "state": "pending"},
]
BUILD_STATES = {"pending", "active", "done", "blocked", "error"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def _read_json_file(path: Path, default):
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return default
    return default


def _write_local_config(path: Path, data: dict) -> None:
    """Write a known local Catalyst config file under .catalyst/ only."""
    path = path.resolve()
    base = CATALYST_DIR.resolve()
    try:
        path.relative_to(base)
    except ValueError:
        raise ValueError("config path escaped .catalyst")
    CATALYST_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _permissions() -> dict:
    data = _read_json_file(PERMISSIONS_FILE, {})
    if not isinstance(data, dict):
        data = {}
    mode = data.get("mode")
    if mode not in PERMISSION_MODES:
        return {
            "mode": "unset",
            "label": "No scan permission selected",
            "manual_paths": [],
            "exclusions": [
                "secrets",
                "tokens",
                "private DMs",
                "client data",
                "binaries",
                "vendor/build folders",
                "sensitive material",
            ],
            "updated_at": None,
        }
    data.setdefault("manual_paths", [])
    data.setdefault("exclusions", [
        "secrets",
        "tokens",
        "private DMs",
        "client data",
        "binaries",
        "vendor/build folders",
        "sensitive material",
    ])
    return data


def _save_permissions(data: dict) -> dict:
    mode = (data.get("mode") or "").strip().lower()
    if mode not in PERMISSION_MODES:
        return {"error": "mode must be one of: recommended, manual, skip"}
    manual_paths = data.get("manual_paths") or []
    if not isinstance(manual_paths, list):
        manual_paths = []
    clean_paths = [str(p).strip() for p in manual_paths if str(p).strip()]
    labels = {
        "recommended": "Recommended safe scan",
        "manual": "Manual paths only",
        "skip": "Skip scan / use typed context",
    }
    payload = {
        "mode": mode,
        "label": labels[mode],
        "manual_paths": clean_paths[:50],
        "exclusions": [
            "secrets",
            "tokens",
            "private DMs",
            "client data",
            "binaries",
            "vendor/build folders",
            "sensitive material",
        ],
        "notes": str(data.get("notes") or "")[:2000],
        "updated_at": _now_iso(),
    }
    _write_local_config(PERMISSIONS_FILE, payload)
    return payload


def _safe_agent_status() -> dict:
    data = _read_json_file(AGENT_STATUS_FILE, {})
    if not isinstance(data, dict):
        return {}
    allowed = {}
    for key in ("agent", "status", "message", "updated_at"):
        if key in data:
            allowed[key] = str(data[key])[:500]
    return allowed


def _setup_prompt(repo_path: str, client: str) -> str:
    repo = repo_path.replace("\\", "/")
    return f"""Set up Catalyst for me and build my Catalyst Brain.

Repository: {repo}
Client: {client}

1. Read README.md, AGENTS.md, and REPO-USE-PROMPT.md in the repository.
2. Read .catalyst/permissions.json if it exists. If it explicitly allows the recommended safe scan, do not ask the approval question again. If it says manual or skip, follow that choice.
3. Discover candidate sources with tools/discover_sessions.py. Discovery is read-only path metadata only.
4. Read file contents only inside the approved scope. Always exclude secrets, tokens, private DMs, client data, binaries, vendor/build folders, and sensitive material.
5. Build everything locally under outputs/<name>/:
   - BUILD-STATUS.json
   - SUMMARY.md
   - catalyst-brain/
   - skills/
   - workflows/
   - evals/
   - proposed-updates/
6. While building, keep outputs/<name>/BUILD-STATUS.json updated with the schema in AGENTS.md so the Catalyst command center can show progress.
7. After the brain is ready, use the Catalyst loop on real work: route_task -> get_context_packet -> produce -> review_output_against_brain -> append_feedback on corrections -> audit_brain.

The local UI is only the command center. You are the v0 builder. Do not overwrite templates/ and do not create a fake hosted integration."""


def _connect_prompts() -> dict:
    repo = str(REPO_ROOT)
    repo_fwd = repo.replace("\\", "/")
    py_cmd = "py" if os.name == "nt" else "python3"
    mcp_args = [str((REPO_ROOT / "tools" / "mcp_server.py").resolve())]
    mcp_config = {
        "mcpServers": {
            "catalyst": {
                "command": py_cmd,
                "args": mcp_args,
                "cwd": repo,
            }
        }
    }
    command_by_id = {
        "claude-code": f'claude mcp add catalyst -s user -- {py_cmd} "{repo_fwd}/tools/mcp_server.py"',
        "codex": f'cd "{repo}" && codex',
        "cursor": f'cursor "{repo}"',
        "hermes": f'cd "{repo}" && hermes',
    }
    clients = []
    for cid, label, binary, setup in AGENT_CLIS:
        found = shutil.which(binary) is not None
        clients.append({
            "id": cid,
            "label": label,
            "detected": found,
            "status": "detected" if found else "not_detected",
            "command": command_by_id.get(cid) if found or cid == "claude-code" else "",
            "command_label": "Install MCP server" if cid == "claude-code" else "Open this agent in the repo",
            "prompt": _setup_prompt(repo, label),
            "setup": setup,
            "mcp_config": mcp_config,
            "live": False,
            "note": "Instructions only. Catalyst does not run this agent from the browser.",
        })
    clients.append({
        "id": "manual-mcp",
        "label": "Manual MCP",
        "detected": True,
        "status": "ready",
        "command": f'{py_cmd} "{repo_fwd}/tools/mcp_server.py"',
        "command_label": "MCP stdio command",
        "prompt": _setup_prompt(repo, "Manual MCP client"),
        "setup": "Add the JSON config to any MCP client, then paste the setup prompt into your agent.",
        "mcp_config": mcp_config,
        "live": False,
        "note": "Manual configuration fallback. No OAuth or hosted connector is implied.",
    })
    return {
        "repo_root": repo,
        "server_url": f"http://{HOST}:{PORT}",
        "permissions": _permissions(),
        "clients": clients,
        "manual_mcp": mcp_config,
    }


def _default_build_status(name: str, exists: bool = False) -> dict:
    slug = _slug(name or "me")
    return {
        "name": slug,
        "status": "waiting",
        "step": "connect_agent",
        "message": "Waiting for your agent to build your Catalyst Brain. Paste the setup prompt into your agent; this page updates automatically.",
        "progress": 0.0,
        "updated_at": None,
        "exists": exists,
        "steps": [dict(step) for step in BUILD_STEPS],
    }


def _build_status(name: str) -> dict:
    slug = _slug(name or "me")
    path = _safe_path(f"outputs/{slug}/BUILD-STATUS.json", READ_ROOTS)
    if not path or not path.is_file():
        return _default_build_status(slug, exists=False)
    raw = _read_json_file(path, {})
    if not isinstance(raw, dict):
        status = _default_build_status(slug, exists=True)
        status.update({
            "status": "error",
            "step": "read_status",
            "message": "BUILD-STATUS.json exists but is not valid JSON.",
            "exists": True,
        })
        return status
    status = _default_build_status(raw.get("name") or slug, exists=True)
    status.update({
        "name": _slug(str(raw.get("name") or slug)),
        "status": str(raw.get("status") or "building"),
        "step": str(raw.get("step") or status["step"]),
        "message": str(raw.get("message") or status["message"]),
        "progress": raw.get("progress", 0.0),
        "updated_at": raw.get("updated_at"),
        "exists": True,
    })
    try:
        status["progress"] = max(0.0, min(1.0, float(status["progress"])))
    except (TypeError, ValueError):
        status["progress"] = 0.0
    steps = raw.get("steps")
    if isinstance(steps, list):
        clean = []
        for step in steps:
            if not isinstance(step, dict):
                continue
            state = step.get("state") if step.get("state") in BUILD_STATES else "pending"
            clean.append({
                "id": str(step.get("id") or "")[:80],
                "label": str(step.get("label") or step.get("id") or "")[:120],
                "state": state,
            })
        if clean:
            status["steps"] = clean
    if status["status"] not in {"waiting", "building", "ready", "blocked", "error"}:
        status["status"] = "building"
    return status


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


def _agent_status() -> dict:
    """Report available AI/agent connection modes. Detection is existence-only
    (shutil.which); nothing is executed. CLI 'detected' does not imply logged in."""
    cfg = byok.get_config()
    modes = []
    # always-on modes
    modes.append({
        "id": "mock", "label": "Mock / offline", "kind": "mock", "status": "ready",
        "live": False,
        "detail": "Demo only. No network. Deterministic placeholder synthesis.",
        "setup": "Always available. Use to explore the flow without a model.",
    })
    modes.append({
        "id": "byok", "label": "OpenRouter (BYOK)", "kind": "byok",
        "status": "ready" if cfg["has_key"] else "needs_key",
        "live": bool(cfg["has_key"]),
        "detail": "Real synthesis/evaluation. Sends only approved text to OpenRouter.",
        "setup": "Set OPENROUTER_API_KEY in .env (env only, never committed), then restart.",
    })
    for mid, label, binary, setup in AGENT_CLIS:
        found = shutil.which(binary) is not None
        modes.append({
            "id": mid, "label": label, "kind": "cli",
            "status": "detected" if found else "not_installed",
            "live": False,  # detection != execution in v0.3
            "detail": ("Found on PATH (login state unknown). v0.3 detects only; "
                       "it does not run the CLI for you yet.") if found
                      else "Not found on PATH.",
            "setup": setup,
        })
    modes.append({
        "id": "manual", "label": "Manual LLM prompt", "kind": "manual", "status": "ready",
        "live": False,
        "detail": "Copy a prompt into any LLM (Claude/ChatGPT/Codex), paste the result back.",
        "setup": "Always available. Best no-key path to real synthesis.",
    })
    any_live = any(m["live"] for m in modes)
    return {"modes": modes, "any_live": any_live, "byok_has_key": cfg["has_key"]}


def _sanitize_filename(name: str) -> str:
    base = os.path.basename((name or "").replace("\\", "/"))
    keep = [c if (c.isalnum() or c in "-_. ") else "-" for c in base]
    s = "".join(keep).strip().strip(".") or "context"
    return s[:80]


def _save_context(name: str, payload: dict) -> dict:
    """Save pasted context / packet / approved paths under outputs/<slug>/sources/.
    Writes are confined to outputs/ only."""
    slug = _slug(name)
    base = _safe_path(f"outputs/{slug}/sources", WRITE_ROOTS)
    if base is None:
        return {"error": "invalid name"}
    base.mkdir(parents=True, exist_ok=True)
    written = []
    text = (payload.get("text") or "").strip()
    if text:
        fn = _sanitize_filename(payload.get("filename") or "pasted-context.md")
        if not fn.endswith((".md", ".txt", ".json", ".jsonl", ".csv")):
            fn += ".md"
        (base / fn).write_text(text, encoding="utf-8")
        written.append(f"sources/{fn}")
    packet = (payload.get("packet") or "").strip()
    if packet:
        (base / "context-packet.md").write_text(packet, encoding="utf-8")
        written.append("sources/context-packet.md")
    paths = payload.get("paths") or []
    if isinstance(paths, list) and paths:
        lines = ["# approved manual source paths", "",
                 "These are paths the user named for later scanning. Not read yet.", ""]
        lines += [f"- {str(p)}" for p in paths if str(p).strip()]
        (base / "approved-paths.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        written.append("sources/approved-paths.md")
    return {"ok": True, "slug": slug, "written": written}


def _import_files(name: str, files: list) -> dict:
    """Write dropped context files under outputs/<slug>/sources/. Confined to outputs/.

    Filenames are sanitized and re-resolved against the allowlist, so traversal is
    blocked twice. Each file is capped to keep the brain lean.
    """
    slug = _slug(name)
    base = _safe_path(f"outputs/{slug}/sources", WRITE_ROOTS)
    if base is None:
        return {"error": "invalid name"}
    base.mkdir(parents=True, exist_ok=True)
    written, skipped = [], []
    for f in (files or []):
        fn = _sanitize_filename((f or {}).get("filename") or "")
        text = (f or {}).get("text") or ""
        if not fn:
            skipped.append("(unnamed)")
            continue
        if not fn.endswith((".md", ".txt", ".json", ".jsonl", ".csv")):
            fn += ".md"
        target = _safe_path(f"outputs/{slug}/sources/{fn}", WRITE_ROOTS)
        if target is None:
            skipped.append(fn)
            continue
        target.write_text(text[:200000], encoding="utf-8")
        written.append(f"sources/{fn}")
    return {"ok": True, "slug": slug, "written": written, "skipped": skipped}


def _import_extract(name: str, mode: str) -> dict:
    """Assemble the no-key extraction prompt + list imported sources. Writes nothing.

    Brain content is written later via paste-back onboarding. With a BYOK key and
    mode='byok', returns a synthesis draft for review (still not auto-applied).
    """
    slug = _slug(name)
    src = REPO_ROOT / "outputs" / slug / "sources"
    sources = sorted(p.name for p in src.glob("*")) if src.is_dir() else []
    cfg = byok.get_config()
    live = mode == "byok" and cfg["has_key"]
    result = {"slug": slug, "mode": mode, "live": live, "sources": sources, "prompt": EXTRACTION_PROMPT}
    if live:
        material = ""
        for p in (src.glob("*") if src.is_dir() else []):
            try:
                material += f"\n\n# {p.name}\n" + p.read_text(encoding="utf-8")[:20000]
            except Exception:
                pass
        result["synthesis"] = byok.get_provider().complete(
            "Extract a Catalyst brain (identity/standards/judgment/taste/voice) from the user's "
            "context. Markdown only, specific, no slop, no overclaiming.",
            material or "(no imported sources yet)")
    return result


def _build_stages(name: str, mode: str) -> dict:
    """Ensure the brain exists and return an honest staged build log. Synthesis is
    NOT run over the network here; live synthesis stays an explicit BYOK action."""
    slug = _slug(name)
    dest = REPO_ROOT / "outputs" / slug
    exists = (dest / "catalyst-brain").is_dir()
    has_sources = (dest / "sources").is_dir()
    live = mode == "byok" and byok.get_config()["has_key"]
    seed_label = "live (BYOK)" if live else "mock / no-key seed"
    stages = [
        ("Preparing source packet", "done" if has_sources else "skipped",
         "imported context found" if has_sources else "no imported context; using typed answers"),
        ("Synthesizing identity / context", "done", seed_label),
        ("Extracting standards / judgment", "done", seed_label),
        ("Extracting rejected examples / anti-slop", "done", seed_label),
        ("Writing skills / workflows / evals", "done" if exists else "pending",
         "templates copied to outputs/" ),
        ("Running first proof setup", "ready", "open the Proof step"),
    ]
    return {"slug": slug, "brain_exists": exists, "mode": mode, "live": live,
            "seed_label": seed_label, "stages": [
                {"name": n, "status": s, "detail": d} for n, s, d in stages]}


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
        # legacy vanilla panel stays reachable at /legacy
        if path == "/legacy" or path.startswith("/legacy/"):
            return self._serve_from(STATIC_DIR, path[len("/legacy"):].lstrip("/") or "index.html", spa=False)
        # prefer the prebuilt consumer UI when present
        if (DIST_DIR / "index.html").is_file():
            return self._serve_from(DIST_DIR, path.lstrip("/") or "index.html", spa=True)
        # fallback before Phase 3 ships: the existing vanilla panel
        return self._serve_from(STATIC_DIR, path.lstrip("/") or "index.html", spa=False)

    def _serve_from(self, base: Path, rel: str, spa: bool):
        target = (base / rel).resolve()
        try:
            target.relative_to(base)
        except ValueError:
            return self._send(403, b"forbidden", "text/plain")
        if not target.is_file():
            # SPA client-side routes (no file extension) fall back to index.html
            if spa and "." not in rel.split("/")[-1]:
                target = base / "index.html"
                if not target.is_file():
                    return self._send(404, b"not found", "text/plain")
            else:
                return self._send(404, b"not found", "text/plain")
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".mjs": "text/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".ico": "image/x-icon",
            ".woff2": "font/woff2",
            ".woff": "font/woff",
            ".map": "application/json",
        }.get(target.suffix, "application/octet-stream")
        self._send(200, target.read_bytes(), ctype)

    # -- GET api --
    def _api_get(self, path: str, q: dict):
        if path == "/api/status":
            cfg = byok.get_config()
            brains = _list_brains()
            return self._json({
                "repo_root": str(REPO_ROOT),
                "brains": brains,
                "active_brain": brains[0]["name"] if brains else "",
                "permissions": _permissions(),
                "agent_status": _safe_agent_status(),
                "runtime_health": runtime_health.get_health(None),
                "recent_captures": runtime_events.list_events(None, limit=10),
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
        if path == "/api/agents/status":
            status = _agent_status()
            status["agent_status"] = _safe_agent_status()
            return self._json(status)
        if path == "/api/connect/prompts":
            return self._json(_connect_prompts())
        if path == "/api/permissions":
            return self._json(_permissions())
        if path == "/api/build/status":
            name = (q.get("name") or [""])[0]
            if not name:
                brains = _list_brains()
                name = brains[0]["name"] if brains else "me"
            return self._json(_build_status(name))
        if path == "/api/health":
            project = (q.get("project") or [""])[0] or None
            return self._json(runtime_health.get_health(project))
        if path == "/api/runtime/health":
            project = (q.get("project") or [""])[0] or "default"
            report = runtime_health.get_health(project)
            report["history"] = versioning.list_history(limit=20)
            report["brain"] = brain_manager.brain_sections_summary(project)
            return self._json(report)
        if path == "/api/brain/sections":
            project = (q.get("project") or [""])[0] or "default"
            return self._json(brain_manager.brain_sections_summary(project))
        if path == "/api/proposals":
            project = (q.get("project") or [""])[0] or None
            status = (q.get("status") or ["pending"])[0]
            try:
                limit = int((q.get("limit") or ["50"])[0])
            except (TypeError, ValueError):
                limit = 50
            return self._json({
                "project": project or "all",
                "status": status or "all",
                "proposals": proposal_engine.list_brain_updates(project=project, status=status or None, limit=limit),
            })
        if path == "/api/events":
            project = (q.get("project") or [""])[0] or None
            return self._json({"events": runtime_events.list_events(project, limit=50)})
        if path == "/api/signals":
            project = (q.get("project") or [""])[0] or None
            return self._json({"signals": runtime_signals.list_signals(project, limit=100)})
        if path == "/api/memories":
            project = (q.get("project") or [""])[0] or None
            query = (q.get("query") or [""])[0]
            if query:
                memories = runtime_memory.search_memories(query, project, limit=50)
            else:
                memories = runtime_memory.list_memories(project, limit=100)
            return self._json({"memories": memories})
        if path == "/api/graph":
            project = (q.get("project") or [""])[0] or None
            graph = runtime_graph.load_graph()
            if not graph.get("nodes"):
                graph = runtime_graph.build_graph(project)
            return self._json({"summary": runtime_graph.graph_summary(project), "graph": graph})
        if path == "/api/extraction-prompt":
            return self._json({"prompt": EXTRACTION_PROMPT})
        if path == "/api/brain":
            name = (q.get("name") or [""])[0]
            brain = (REPO_ROOT / "outputs" / name / "catalyst-brain")
            if not _safe_path(f"outputs/{name}/catalyst-brain", READ_ROOTS) or not brain.is_dir():
                return self._json({"error": "brain not found"}, 404)
            files = {}
            for f in BRAIN_FILE_ORDER:
                p = brain / f
                if not p.is_file():
                    continue
                files[f] = _parse_brain_meta(p.read_text(encoding="utf-8"))
            groups = []
            for label, names in BRAIN_GROUPS:
                items = [{"file": f, "meta": files[f]} for f in names if f in files]
                if items:
                    groups.append({"label": label, "files": items})
            # any files not in a group (e.g. README) appended under "Index"
            grouped = {f for _, ns in BRAIN_GROUPS for f in ns}
            extra = [{"file": f, "meta": files[f]} for f in BRAIN_FILE_ORDER if f in files and f not in grouped]
            if extra:
                groups.insert(0, {"label": "Index", "files": extra})
            return self._json({"name": name, "groups": groups,
                               "files": [{"file": f, "meta": m} for f, m in files.items()]})
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
        if path == "/api/flow/route":
            name = (q.get("name") or [""])[0]
            task = (q.get("task") or [""])[0]
            if not name or not task:
                return self._json({"error": "name and task required"}, 400)
            return self._json(flow_router.route_task(name, task))
        if path == "/api/flow/audit":
            name = (q.get("name") or [""])[0]
            if not name:
                return self._json({"error": "name required"}, 400)
            return self._json(flow_quality.audit_brain(name))
        if path == "/api/import/discover":
            if discover_sessions is None:
                return self._json({"categories": [], "missing_categories": [], "note": "discovery helper unavailable"})
            res = discover_sessions.discover()
            cats = {}
            for item in res.get("found", []):
                cats[item["category"]] = cats.get(item["category"], 0) + 1
            return self._json({
                "categories": [{"category": c, "count": n} for c, n in sorted(cats.items())],
                "missing_categories": res.get("missing_categories", []),
                "note": "read-only path discovery. nothing was read. you approve any import.",
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
        if path == "/api/context/save":
            name = data.get("name", "")
            if not name.strip():
                return self._json({"error": "name is required"}, 400)
            res = _save_context(name, data)
            code = 200 if res.get("ok") else 400
            return self._json(res, code)
        if path == "/api/permissions":
            res = _save_permissions(data)
            return self._json(res, 400 if res.get("error") else 200)
        if path == "/api/build":
            name = data.get("name", "")
            if not name.strip():
                return self._json({"error": "name is required"}, 400)
            # ensure a brain exists (scaffold from answers if not yet built)
            slug = _slug(name)
            if not (REPO_ROOT / "outputs" / slug / "catalyst-brain").is_dir():
                _scaffold_brain(name, data.get("answers", {}) or {})
            result = _build_stages(name, data.get("mode", "mock"))
            result["brains"] = _list_brains()
            return self._json(result)
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
        if path == "/api/flow/context":
            name, task = data.get("name", ""), data.get("task", "")
            if not name or not task:
                return self._json({"error": "name and task required"}, 400)
            return self._json({"packet": flow_packet.build_context_packet(name, task, data.get("mode", "auto"))})
        if path == "/api/flow/evaluate":
            name, task = data.get("name", ""), data.get("task", "")
            if not name or not task:
                return self._json({"error": "name and task required"}, 400)
            return self._json(flow_evaluator.evaluate_output(name, task, data.get("output", ""), data.get("mode", "auto")))
        if path == "/api/flow/feedback":
            name, task = data.get("name", ""), data.get("task", "")
            if not name or not task:
                return self._json({"error": "name and task required"}, 400)
            res = flow_feedback.capture_feedback(name, task, data.get("output", ""), data.get("feedback", ""))
            return self._json(res, 200 if res.get("ok") else 400)
        if path == "/api/brain/context":
            task = data.get("task", "")
            if not task:
                return self._json({"error": "task required"}, 400)
            return self._json(context_assembler.assemble_context(
                task,
                project=data.get("project") or "default",
                agent=data.get("agent") or "api",
            ))
        if path == "/api/evaluate":
            task = data.get("task", "")
            if not task:
                return self._json({"error": "task required"}, 400)
            return self._json(structured_evaluator.evaluate_output_structured(
                task,
                data.get("output", ""),
                project=data.get("project") or "default",
            ))
        if path == "/api/feedback":
            task = data.get("task", "")
            feedback = data.get("feedback", "")
            if not task or not feedback:
                return self._json({"error": "task and feedback required"}, 400)
            res = feedback_processor.capture_feedback_structured(
                task,
                data.get("output", ""),
                feedback,
                project=data.get("project") or "default",
                source=data.get("source") or "api",
            )
            return self._json(res, 200 if res.get("ok") else 400)
        if path == "/api/proposals/apply":
            proposal_id = data.get("proposal_id") or data.get("id") or ""
            if not proposal_id:
                return self._json({"error": "proposal_id required"}, 400)
            res = proposal_engine.apply_brain_update(
                proposal_id,
                project=data.get("project") or "default",
                approve=bool(data.get("approve", True)),
            )
            return self._json(res, 200 if res.get("ok") else 400)
        if path == "/api/recall":
            task = data.get("task", "")
            if not task:
                return self._json({"error": "task required"}, 400)
            return self._json(runtime_recall.build_context_packet(
                task,
                data.get("project") or "default",
                data.get("agent") or "api",
            ))
        if path == "/api/capture":
            event = data.get("event") if isinstance(data.get("event"), dict) else data
            res = runtime_capture.capture_event(event)
            return self._json(res, 200 if res.get("ok") else 400)
        if path == "/api/review":
            task = data.get("task", "")
            if not task:
                return self._json({"error": "task required"}, 400)
            return self._json(runtime_judgment.review_output(
                task,
                data.get("output", ""),
                data.get("project") or "default",
            ))
        if path == "/api/import/files":
            name = data.get("name", "")
            if not name.strip():
                return self._json({"error": "name is required"}, 400)
            res = _import_files(name, data.get("files") or [])
            return self._json(res, 200 if res.get("ok") else 400)
        if path == "/api/import/extract":
            name = data.get("name", "")
            if not name.strip():
                return self._json({"error": "name is required"}, 400)
            return self._json(_import_extract(name, data.get("mode", "manual")))
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
    try:
        httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as exc:
        print(f"Could not start Catalyst on http://{HOST}:{PORT}.", file=sys.stderr)
        print(f"Reason: {exc}", file=sys.stderr)
        if "address already in use" in str(exc).lower() or getattr(exc, "winerror", None) == 10048:
            print("Port 8765 is already in use. Stop the other Catalyst/Python process or set CATALYST_PORT to another port.", file=sys.stderr)
        return 2
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
