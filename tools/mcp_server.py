"""mcp_server.py — Catalyst brain access for agents (dependency-free scaffold).

This is a MINIMAL, honest scaffold — not a fully certified MCP implementation.
It speaks JSON-RPC 2.0 over stdio and implements the core MCP methods
(`initialize`, `tools/list`, `tools/call`) plus five allowlisted Catalyst tools.
Python standard library only, local stdio only, no network.

Tools (all confined to outputs/<name>/):
- list_brain_sections(name)            -> grouped section index
- read_brain_section(name, file)       -> one brain file's markdown
- review_output_against_brain(name, task, draft)
                                        -> deterministic local standards checklist
- append_feedback(name, note)          -> append to catalyst-brain/feedback-memory.md
- propose_brain_update(name, file, suggestion)
                                        -> write a PROPOSAL under proposed-updates/ (never overwrites the brain)

Security:
- read access limited to outputs/<name>/catalyst-brain/*.md
- write access ONLY via append_feedback and propose_brain_update, confined to outputs/
- no arbitrary path access, no shell, no network

Run (stdio):
    py tools/mcp_server.py
Connect from an MCP client by pointing it at that command. See docs/mcp.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = REPO_ROOT / "outputs"

sys.path.insert(0, str(REPO_ROOT))
from catalyst_core import (  # noqa: E402
    router as core_router,
    packet as core_packet,
    evaluator as core_evaluator,
    feedback as core_feedback,
    quality as core_quality,
)

BRAIN_GROUPS = [
    ("Identity / context", ["identity.md", "context.md", "goals.md", "constraints.md"]),
    ("Taste / judgment", ["standards.md", "judgment.md", "taste.md", "anti-slop.md", "rejected-examples.md"]),
    ("Operating logic", ["decision-rules.md", "task-patterns.md", "voice.md", "lexicon.md", "references.md"]),
    ("Learning", ["feedback-memory.md", "open-questions.md"]),
]
REVIEW_FILES = ["standards.md", "judgment.md", "identity.md", "constraints.md",
                "rejected-examples.md", "taste.md", "task-patterns.md"]


def _slug(name: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in (name or "").strip()]
    s = "".join(keep)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-") or "me"


def _brain_dir(name: str) -> Path | None:
    d = (OUTPUTS / _slug(name) / "catalyst-brain").resolve()
    try:
        d.relative_to(OUTPUTS.resolve())
    except ValueError:
        return None
    return d if d.is_dir() else None


def _safe_brain_file(name: str, file: str) -> Path | None:
    if not file or "/" in file or "\\" in file or ".." in file or not file.endswith(".md"):
        return None
    bd = _brain_dir(name)
    if bd is None:
        return None
    p = (bd / file).resolve()
    try:
        p.relative_to(bd)
    except ValueError:
        return None
    return p


# --- tools -------------------------------------------------------------------
def list_brain_sections(name: str) -> dict:
    bd = _brain_dir(name)
    if bd is None:
        return {"error": f"no brain for '{name}'"}
    present = {p.name for p in bd.glob("*.md")}
    groups = []
    for label, files in BRAIN_GROUPS:
        items = [f for f in files if f in present]
        if items:
            groups.append({"group": label, "files": items})
    return {"name": name, "groups": groups, "count": len(present)}


def read_brain_section(name: str, file: str) -> dict:
    p = _safe_brain_file(name, file)
    if p is None or not p.is_file():
        return {"error": "section not found or not allowed"}
    return {"name": name, "file": file, "content": p.read_text(encoding="utf-8")}


def review_output_against_brain(name: str, task: str = "", draft: str = "") -> dict:
    """Real deterministic evaluation via catalyst_core (verdict + scores + issues)."""
    if _brain_dir(name) is None:
        return {"error": f"no brain for '{name}'"}
    return core_evaluator.evaluate_output(name, task, draft)


def append_feedback(name: str, note: str, task: str = "(via mcp)") -> dict:
    """Compound a correction through catalyst_core: append feedback-memory +
    improvement-log and write a review proposal (never silently overwrites)."""
    if not (note or "").strip():
        return {"error": "empty feedback"}
    return core_feedback.capture_feedback(name, task, "", note)


def propose_brain_update(name: str, file: str, suggestion: str) -> dict:
    """Write a PROPOSAL, never overwrite the brain. Proposals land in
    outputs/<name>/proposed-updates/ for human/agent review."""
    if not file or not file.endswith(".md") or "/" in file or "\\" in file or ".." in file:
        return {"error": "invalid target file"}
    base = (OUTPUTS / _slug(name)).resolve()
    try:
        base.relative_to(OUTPUTS.resolve())
    except ValueError:
        return {"error": "invalid name"}
    if not (base / "catalyst-brain").is_dir():
        return {"error": f"no brain for '{name}'"}
    pdir = base / "proposed-updates"
    pdir.mkdir(parents=True, exist_ok=True)
    target = pdir / file
    block = (f"# proposed update -> catalyst-brain/{file}\n\n"
             "Not applied. Review and merge manually or via the update workflow.\n\n"
             f"{(suggestion or '').strip()}\n")
    existing = target.read_text(encoding="utf-8") + "\n\n---\n\n" if target.is_file() else ""
    target.write_text(existing + block, encoding="utf-8")
    return {"ok": True, "file": f"proposed-updates/{file}", "applied": False}


def get_context_packet(name: str, task: str = "", mode: str = "auto") -> dict:
    """Build the full context packet (identity/standards/judgment/taste + judgment contract)."""
    if _brain_dir(name) is None:
        return {"error": f"no brain for '{name}'"}
    return {"name": name, "task": task, "packet": core_packet.build_context_packet(name, task, mode)}


def route_task(name: str, task: str = "") -> dict:
    """Classify a task and return the brain files to load, with reasons + warnings."""
    return core_router.route_task(name, task)


def audit_brain(name: str) -> dict:
    """Self-audit the brain: readiness, thin/stale/duplicate flags, distill recommendation."""
    return core_quality.audit_brain(name)


TOOLS = {
    "list_brain_sections": {
        "fn": list_brain_sections,
        "description": "List the brain's sections grouped by job.",
        "schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    "read_brain_section": {
        "fn": read_brain_section,
        "description": "Read one brain file (e.g. standards.md).",
        "schema": {"type": "object", "properties": {"name": {"type": "string"}, "file": {"type": "string"}}, "required": ["name", "file"]},
    },
    "review_output_against_brain": {
        "fn": review_output_against_brain,
        "description": "Return the standards checklist + which brain files load for a task.",
        "schema": {"type": "object", "properties": {"name": {"type": "string"}, "task": {"type": "string"}, "draft": {"type": "string"}}, "required": ["name"]},
    },
    "append_feedback": {
        "fn": append_feedback,
        "description": "Capture a correction: append feedback-memory + improvement-log and write a review proposal.",
        "schema": {"type": "object", "properties": {"name": {"type": "string"}, "note": {"type": "string"}, "task": {"type": "string"}}, "required": ["name", "note"]},
    },
    "propose_brain_update": {
        "fn": propose_brain_update,
        "description": "Write a proposed brain edit (never overwrites the brain).",
        "schema": {"type": "object", "properties": {"name": {"type": "string"}, "file": {"type": "string"}, "suggestion": {"type": "string"}}, "required": ["name", "file", "suggestion"]},
    },
    "get_context_packet": {
        "fn": get_context_packet,
        "description": "Build the full context packet (identity/standards/judgment/taste + judgment contract) for a task.",
        "schema": {"type": "object", "properties": {"name": {"type": "string"}, "task": {"type": "string"}, "mode": {"type": "string"}}, "required": ["name"]},
    },
    "route_task": {
        "fn": route_task,
        "description": "Classify a task and return the brain files to load.",
        "schema": {"type": "object", "properties": {"name": {"type": "string"}, "task": {"type": "string"}}, "required": ["name"]},
    },
    "audit_brain": {
        "fn": audit_brain,
        "description": "Self-audit the brain: readiness, thin/stale/duplicate flags, distill recommendation.",
        "schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
}


def _tool_list() -> list:
    return [{"name": k, "description": v["description"], "inputSchema": v["schema"]} for k, v in TOOLS.items()]


# Standing directive surfaced to the agent on connect (MCP `initialize.instructions`).
# This is what makes "connect MCP -> the agent does the rest" real: the client injects
# these instructions, so the agent knows to scan, build, and run the brain via AGENTS.md.
CATALYST_INSTRUCTIONS = (
    "You are connected to Catalyst, the user's local judgment brain. Before substantive work, "
    "operate it like this:\n"
    "1. Read AGENTS.md and README.md in this repo for the full protocol.\n"
    "2. Read .catalyst/permissions.json if present. If it explicitly approves the recommended safe scan, "
    "do not ask the approval question again; otherwise ask one compact approval question.\n"
    "3. Discover where the user's AI sessions, notes, exports, and workspaces live "
    "(tools/discover_sessions.py); do not read contents until the scan scope is approved.\n"
    "4. Build the user's Catalyst brain under outputs/<name>/ from the approved material. Keep "
    "outputs/<name>/BUILD-STATUS.json updated while working, then write SUMMARY.md plus the personalized "
    "skills/workflows/evals/proposed-updates. Never overwrite anything under templates/.\n"
    "5. For each task: call route_task, then get_context_packet (load the brain + judgment contract) "
    "before producing; after producing call review_output_against_brain; on a correction call "
    "append_feedback (writes a proposal, never a silent overwrite); periodically call audit_brain to "
    "keep the brain sharp.\n"
    "Run the 'catalyst-build-and-run' prompt to kick this off."
)

BUILD_AND_RUN_PROMPT = (
    "Read README.md and AGENTS.md in this repo. Use it to build my Catalyst brain.\n"
    "First read .catalyst/permissions.json if present, then discover where my AI sessions, notes, exports, "
    "agent memories, and workspaces live. Do not read file contents yet. Show me the discovered locations, "
    "recommend a safe scan scope, and ask what you may scan if I have not already authorized it; then audit only the approved scope.\n"
    "Extract identity/context/standards/judgment/taste/feedback with evidence, create files under "
    "outputs/<name>/, keep BUILD-STATUS.json updated while you work, write Catalyst skills/workflows/evals, "
    "and write outputs/<name>/SUMMARY.md explaining how to use the brain. Then run my real tasks through the loop: "
    "route_task -> get_context_packet -> produce -> review_output_against_brain -> append_feedback on my "
    "corrections -> audit_brain to keep it sharp. Compound session to session."
)

PROMPTS = {
    "catalyst-build-and-run": {
        "description": "Build the user's Catalyst brain from their context, then run + improve it through the loop.",
        "text": BUILD_AND_RUN_PROMPT,
    },
}


def handle(req: dict) -> dict | None:
    """Dispatch one JSON-RPC request. Returns a response dict (or None for notifications)."""
    method = req.get("method")
    rid = req.get("id")
    params = req.get("params") or {}

    def ok(result):
        return {"jsonrpc": "2.0", "id": rid, "result": result}

    def err(code, msg):
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": msg}}

    if method == "initialize":
        return ok({"protocolVersion": "2024-11-05",
                   "serverInfo": {"name": "catalyst-brain", "version": "0.4"},
                   "instructions": CATALYST_INSTRUCTIONS,
                   "capabilities": {"tools": {}, "prompts": {}}})
    if method in ("notifications/initialized", "initialized"):
        return None
    if method == "tools/list":
        return ok({"tools": _tool_list()})
    if method == "prompts/list":
        return ok({"prompts": [{"name": k, "description": v["description"]} for k, v in PROMPTS.items()]})
    if method == "prompts/get":
        p = PROMPTS.get(params.get("name"))
        if not p:
            return err(-32602, f"unknown prompt: {params.get('name')}")
        return ok({"description": p["description"],
                   "messages": [{"role": "user", "content": {"type": "text", "text": p["text"]}}]})
    if method == "tools/call":
        tname = params.get("name")
        args = params.get("arguments") or {}
        tool = TOOLS.get(tname)
        if not tool:
            return err(-32601, f"unknown tool: {tname}")
        try:
            result = tool["fn"](**args)
        except TypeError as exc:
            return err(-32602, f"bad arguments: {exc}")
        return ok({"content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                   "isError": bool(isinstance(result, dict) and result.get("error"))})
    if rid is None:
        return None
    return err(-32601, f"unknown method: {method}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except ValueError:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None,
                                         "error": {"code": -32700, "message": "parse error"}}) + "\n")
            sys.stdout.flush()
            continue
        resp = handle(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
