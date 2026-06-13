"""discover_sessions.py — read-only cross-system AI-session & workspace discovery.

The agent runs this (or replicates its logic) to FIND where the user's past AI
sessions, exports, notes, and project workspaces live — so the user does not have
to hunt down paths. It only checks whether known locations EXIST and prints them.

It does NOT read file contents, open network connections, upload anything, or
modify anything. It prints local path metadata; if you run it inside a hosted
agent, that metadata may enter that agent/model context. The user approves which
discovered locations to actually scan (see prompts/01-source-audit.md).
Discovery != reading.

Python standard library only. Run:
    python tools/discover_sessions.py
    py tools/discover_sessions.py        (Windows launcher)
"""
import json
import os
from pathlib import Path

HOME = Path.home()


def _exists(p: Path):
    try:
        return p.exists()
    except OSError:
        return False


def _candidates():
    """Return [(category, path, note)] for known AI-session / workspace locations.

    Covers the major agent runtimes and common export/notes/workspace spots on
    Windows, macOS, and Linux. Existence is checked; contents are never read.
    """
    appdata = Path(os.environ.get("APPDATA", HOME / "AppData" / "Roaming"))
    localapp = Path(os.environ.get("LOCALAPPDATA", HOME / "AppData" / "Local"))
    downloads = HOME / "Downloads"
    documents = HOME / "Documents"
    desktop = HOME / "Desktop"

    raw = [
        # --- Claude Code ---
        ("claude-code", HOME / ".claude" / "projects", "Claude Code session transcripts per project"),
        ("claude-code", HOME / ".claude" / "history.jsonl", "Claude Code command history"),
        ("claude-code", HOME / ".claude.json", "Claude Code config + recent project list"),
        ("claude-code", HOME / ".claude" / "todos", "Claude Code todo state"),
        # --- Agent memory / global instructions / generated skills ---
        ("agent-memory", HOME / ".claude" / "CLAUDE.md", "Claude Code global instructions (how you operate)"),
        ("agent-memory", HOME / ".claude" / "skills", "Claude Code generated/installed skills"),
        ("agent-memory", HOME / ".hermes", "Hermes agent sessions / memory (if present)"),
        ("agent-memory", HOME / ".config" / "agent", "generic CLI-agent config/memory (if present)"),
        # --- Cursor ---
        ("cursor", appdata / "Cursor" / "User" / "workspaceStorage", "Cursor per-workspace state (incl. chat)"),
        ("cursor", appdata / "Cursor" / "User" / "globalStorage", "Cursor global state"),
        ("cursor", HOME / ".cursor", "Cursor home config (incl. .cursorrules referenced per-repo)"),
        # --- Codex / Copilot / Gemini / Windsurf / other CLIs ---
        ("codex", HOME / ".codex", "Codex CLI sessions/config"),
        ("copilot", HOME / ".copilot", "Copilot CLI state"),
        ("gemini", HOME / ".gemini", "Gemini CLI state"),
        ("windsurf", HOME / ".codeium" / "windsurf", "Windsurf / Codeium agent state"),
        ("ollama", HOME / ".ollama", "Local Ollama data"),
        # --- ChatGPT / Claude.ai exports (manual data exports usually land here) ---
        ("chatgpt-export", downloads, "look for ChatGPT export zip / conversations.json"),
        ("claude-export", downloads, "look for Claude.ai data export"),
        # --- Notes / knowledge bases ---
        ("obsidian", appdata / "obsidian", "Obsidian vault registry (obsidian.json)"),
        ("notion-export", downloads, "look for Notion 'Export-*.zip'"),
        # --- Project workspaces (markdown-heavy dirs the user works in) ---
        ("workspace", desktop, "Desktop — scan for project folders / markdown"),
        ("workspace", documents, "Documents — scan for project folders / markdown"),
        # --- VS Code (chat/copilot history) ---
        ("vscode", appdata / "Code" / "User" / "workspaceStorage", "VS Code per-workspace storage"),
    ]
    # De-dupe exact duplicate category+path pairs while preserving distinct
    # categories that share a path (Downloads can contain ChatGPT, Claude.ai,
    # and Notion exports, so collapsing by path alone hides coverage).
    seen = set()
    out = []
    for cat, path, note in raw:
        key = (cat, str(path).lower())
        if key in seen:
            continue
        seen.add(key)
        out.append((cat, path, note))
    return out


def discover():
    """Return {"found": [...], "missing_categories": [...]} — paths only, no contents."""
    found = []
    found_categories = set()
    for category, path, note in _candidates():
        if _exists(path):
            found.append({"category": category, "path": str(path), "note": note})
            found_categories.add(category)
    all_categories = {c for c, _, _ in _candidates()}
    missing = sorted(all_categories - found_categories)
    return {"found": found, "missing_categories": missing}


def run(root=None):
    """Eval/test hook: discovery must never raise. Returns [] (no failures) if it runs."""
    try:
        discover()
        return []
    except Exception as exc:  # pragma: no cover
        return ["discover_sessions crashed: %r" % exc]


def main():
    result = discover()
    print("# catalyst - discovered source locations (read-only)\n")
    if not result["found"]:
        print("No known AI-session/workspace locations found in default paths.")
        print("Point the agent at your files manually (see prompts/01-source-audit.md).")
    else:
        print("Found these candidate locations. Nothing was read - you approve the scan scope:\n")
        for item in result["found"]:
            print("  [%s] %s" % (item["category"], item["path"]))
            print("        -> %s" % item["note"])
    if result["missing_categories"]:
        print("\nNot found (skipped): %s" % ", ".join(result["missing_categories"]))
    print("\nNext: tell the agent which of these to scan. It reads only what you approve.")
    # machine-readable tail for agents that prefer JSON
    print("\n---JSON---")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
