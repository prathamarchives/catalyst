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

BRAIN_GROUPS = [
    ("Who / why", ["identity.md", "context.md", "goals.md", "constraints.md"]),
    ("Taste / standards", ["standards.md", "judgment.md", "taste.md", "anti-slop.md", "rejected-examples.md"]),
    ("Operating system", ["decision-rules.md", "task-patterns.md", "voice.md", "lexicon.md", "references.md"]),
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
    bd = _brain_dir(name)
    if bd is None:
        return {"error": f"no brain for '{name}'"}
    loaded = [f for f in REVIEW_FILES if (bd / f).is_file()]
    checklist = [
        f"Does it meet the written bar in standards.md?",
        f"Would judgment.md approve, revise, or reject it?",
        f"Does it avoid everything in rejected-examples.md and anti-slop.md?",
        f"Is it consistent with identity.md and constraints.md?",
        f"Does it follow the relevant pattern in task-patterns.md?",
    ]
    return {
        "name": name, "task": task,
        "loaded_files": loaded,
        "review_checklist": checklist,
        "verdict_options": ["approve", "revise", "reject"],
        "note": "Deterministic local review scaffold. A connected model fills in verdicts; "
                "this server does not call any network.",
        "draft_chars": len(draft or ""),
    }


def append_feedback(name: str, note: str) -> dict:
    bd = _brain_dir(name)
    if bd is None:
        return {"error": f"no brain for '{name}'"}
    if not (note or "").strip():
        return {"error": "empty feedback"}
    fm = bd / "feedback-memory.md"
    block = ("\n\n## feedback (via MCP)\n\n- status: observed\n"
             "  evidence: appended through mcp_server.append_feedback\n"
             f"  rule: {note.strip()}\n")
    existing = fm.read_text(encoding="utf-8") if fm.is_file() else "# feedback-memory\n"
    fm.write_text(existing + block, encoding="utf-8")
    return {"ok": True, "file": "catalyst-brain/feedback-memory.md"}


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
        "description": "Append a feedback rule to feedback-memory.md.",
        "schema": {"type": "object", "properties": {"name": {"type": "string"}, "note": {"type": "string"}}, "required": ["name", "note"]},
    },
    "propose_brain_update": {
        "fn": propose_brain_update,
        "description": "Write a proposed brain edit (never overwrites the brain).",
        "schema": {"type": "object", "properties": {"name": {"type": "string"}, "file": {"type": "string"}, "suggestion": {"type": "string"}}, "required": ["name", "file", "suggestion"]},
    },
}


def _tool_list() -> list:
    return [{"name": k, "description": v["description"], "inputSchema": v["schema"]} for k, v in TOOLS.items()]


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
                   "serverInfo": {"name": "catalyst-brain", "version": "0.3"},
                   "capabilities": {"tools": {}}})
    if method in ("notifications/initialized", "initialized"):
        return None
    if method == "tools/list":
        return ok({"tools": _tool_list()})
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
