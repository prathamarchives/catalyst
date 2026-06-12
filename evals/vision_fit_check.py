"""Eval: the protocol actually delivers the cross-system discovery vision.

The repo's promise is: paste it into your agent, the agent discovers and scans
your past AI sessions / workspaces across the system (with your approval), builds
the brain, and writes a skill that compounds from how you talk and what you
correct, session to session.

This check enforces that the protocol files actually establish that capability --
so a future edit can't quietly regress it back to "ask the user to paste files".
Markers are matched case-insensitively; ANY marker in a group satisfies it.
"""
from pathlib import Path


def _read(root: Path, rel: str) -> str:
    p = root / rel
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8").lower()


def run(root: Path) -> list:
    failures = []

    agents = _read(root, "AGENTS.md")
    audit = _read(root, "prompts/01-source-audit.md")
    start = _read(root, "prompts/00-start-here.md")
    extract = _read(root, "prompts/03-extract-creative-identity.md")
    skill = _read(root, "templates/skills/creative-identity-skill.md")
    readme = _read(root, "README.md")
    use_prompt = _read(root, "REPO-USE-PROMPT.md")
    discovery_corpus = agents + "\n" + audit + "\n" + start

    # (requirement, corpus, marker phrases)
    checks = [
        ("discovery is an explicit step", discovery_corpus, ["discover"]),
        ("names concrete cross-system locations (claude code path)", audit, [".claude", "claude code"]),
        ("covers multiple agent runtimes", audit, ["cursor"]),
        ("covers exports (chatgpt/claude.ai)", audit, ["chatgpt", "export"]),
        ("ingests workspaces / projects, not just chat", audit + extract, ["workspace", "project"]),
        ("discovery is consent-gated (user approves scope)", discovery_corpus, ["approve", "you decide", "confirm the scan", "approve the scope"]),
        ("references the discovery helper", discovery_corpus + readme, ["discover_sessions", "tools/discover"]),
        ("extracts behavior, not just stated preferences", extract + skill, ["behavior", "behaviour", "how you work", "how you talk across"]),
        ("compounds session to session", skill + agents, ["each session", "every session", "session to session", "session-to-session"]),
        ("paste-and-go framing", readme + use_prompt, ["paste"]),
    ]

    for requirement, corpus, markers in checks:
        if not any(m in corpus for m in markers):
            failures.append("vision not established: %s" % requirement)

    # the discovery helper must exist as a real file, not just be referenced
    helper = root / "tools" / "discover_sessions.py"
    if not helper.is_file():
        failures.append("missing discovery helper: tools/discover_sessions.py")
    else:
        helper_text = helper.read_text(encoding="utf-8").lower()
        for marker in ["claude-export", "notion-export", "chatgpt-export", "cursor", "workspace"]:
            if marker not in helper_text:
                failures.append("discovery helper missing category marker: %s" % marker)
        if "str(path).lower()" in helper_text and "cat," not in helper_text:
            failures.append("discovery helper may de-dupe by path only and hide shared-path categories")
        if "path metadata" not in helper_text:
            failures.append("discovery helper does not warn that printed paths are metadata")

    for stale in ["first ask me where my source material is", "start by asking where my source material lives"]:
        if stale in readme + use_prompt + start:
            failures.append('stale manual-first prompt remains: "%s"' % stale)

    return failures


if __name__ == "__main__":
    import sys

    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print("FAIL vision_fit_check: %s" % p)
    if not problems:
        print("PASS vision_fit_check")
    sys.exit(1 if problems else 0)
