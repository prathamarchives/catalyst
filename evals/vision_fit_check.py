from pathlib import Path

def read(root, rel):
    p = root / rel
    return p.read_text(encoding="utf-8").lower() if p.is_file() else ""

def run(root: Path) -> list:
    failures = []
    agents = read(root, "AGENTS.md")
    audit = read(root, "prompts/01-source-audit.md")
    extract = read(root, "prompts/03-extract-catalyst-brain.md")
    skill = read(root, "templates/skills/catalyst-skill.md")
    readme = read(root, "README.md")
    corpus = agents + audit + extract + skill + readme
    checks = [
        ("discovery", ["discover"]),
        ("claude code", ["claude code", ".claude"]),
        ("cursor", ["cursor"]),
        ("exports", ["chatgpt", "export"]),
        ("workspaces", ["workspace"]),
        ("consent gated", ["approve", "authorization"]),
        ("behavior extraction", ["behavior"]),
        ("session compounding", ["session to session", "every session"]),
        ("identity", ["identity"]),
        ("judgment", ["judgment"]),
        ("standards", ["standards"]),
    ]
    for label, markers in checks:
        if not any(m in corpus for m in markers):
            failures.append(f"vision not established: {label}")
    helper = root / "tools" / "discover_sessions.py"
    if not helper.is_file():
        failures.append("missing discovery helper: tools/discover_sessions.py")
    return failures

if __name__ == "__main__":
    import sys
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems: print("FAIL vision_fit_check:", p)
    if not problems: print("PASS vision_fit_check")
    sys.exit(1 if problems else 0)
