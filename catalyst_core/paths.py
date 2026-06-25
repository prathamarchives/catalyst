"""paths.py — shared scope + safety helpers for catalyst_core.

Single source of truth for brain-file ordering, slugging, allowlisted path
resolution, and markdown section parsing. Mirrors the helpers in
apps/control-panel/server.py and tools/mcp_server.py so behavior matches.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = REPO_ROOT / "outputs"
TEMPLATES = REPO_ROOT / "templates"

BRAIN_FILE_ORDER = [
    "README.md", "identity.md", "context.md", "goals.md", "constraints.md",
    "standards.md", "judgment.md", "taste.md", "voice.md", "anti-slop.md",
    "references.md", "rejected-examples.md", "decision-rules.md",
    "task-patterns.md", "feedback-memory.md", "lexicon.md", "open-questions.md",
]

BRAIN_GROUPS = [
    ("Identity / context", ["identity.md", "context.md", "goals.md", "constraints.md"]),
    ("Taste / judgment", ["standards.md", "judgment.md", "taste.md", "anti-slop.md", "rejected-examples.md"]),
    ("Operating logic", ["decision-rules.md", "task-patterns.md", "voice.md", "lexicon.md", "references.md"]),
    ("Learning", ["feedback-memory.md", "open-questions.md"]),
]


def slug(name: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in (name or "").strip()]
    s = "".join(keep)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-") or "me"


def brain_dir(name: str, outputs_root: Path = OUTPUTS) -> Path | None:
    root = Path(outputs_root).resolve()
    d = (root / slug(name) / "catalyst-brain").resolve()
    try:
        d.relative_to(root)
    except ValueError:
        return None
    return d if d.is_dir() else None


def safe_brain_file(name: str, file: str, outputs_root: Path = OUTPUTS) -> Path | None:
    if not file or "/" in file or "\\" in file or ".." in file or not file.endswith(".md"):
        return None
    bd = brain_dir(name, outputs_root)
    if bd is None:
        return None
    p = (bd / file).resolve()
    try:
        p.relative_to(bd)
    except ValueError:
        return None
    return p


def safe_outputs_path(rel: str, outputs_root: Path = OUTPUTS) -> Path | None:
    if rel is None:
        return None
    rel = rel.replace("\\", "/").lstrip("/")
    if ".." in rel.split("/"):
        return None
    root = Path(outputs_root).resolve()
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root)
        return candidate
    except ValueError:
        return None


def parse_sections(text: str) -> dict:
    """Return {header_lower: body} for every '## ' section in a brain file."""
    out: dict = {}
    current = None
    buf: list = []
    for line in (text or "").splitlines():
        if line.startswith("## "):
            if current is not None:
                out[current] = "\n".join(buf).strip()
            current = line[3:].strip().lower()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        out[current] = "\n".join(buf).strip()
    return out


def is_placeholder(text: str) -> bool:
    """True when a brain file is still the unfilled template (no extracted rules)."""
    t = text or ""
    if "seeded from onboarding" in t.lower():
        return False
    rules = parse_sections(t).get("evidence / rules", "")
    if not rules:
        return True
    low = rules.lower()
    return ("status: assumed" in low and "evidence: pending" in low) or \
           "replace with extracted material" in low
