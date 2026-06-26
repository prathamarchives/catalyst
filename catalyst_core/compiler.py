"""Compile memory atoms and persona nodes into a local wiki-style Persona Brain."""
from __future__ import annotations

import re
from pathlib import Path

from . import memory, store, subbrains

ROOT_FILES = {"_index.md", "GRAPH.md", "README.md"}


def _brain_root(state_root: Path = store.STATE_ROOT) -> Path:
    return store.state_path("persona-brain", state_root=state_root)


def _frontmatter(brain: str, maturity: float, confidence: float, sources: list[str]) -> str:
    src = "\n".join(f"  - {s}" for s in sources[:10]) or "  - none-yet"
    return (
        "---\n"
        "type: brain_file\n"
        f"brain: {brain}\n"
        "status: active\n"
        f"maturity: {round(maturity, 2)}\n"
        f"confidence: {round(confidence, 2)}\n"
        f"last_updated: {store.now_iso()[:10]}\n"
        "source_events:\n"
        f"{src}\n"
        "---\n\n"
    )


def _wiki_link(path: str) -> str:
    return f"[[{path[:-3] if path.endswith('.md') else path}]]"


def _write(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def ensure_indexes(state_root: Path = store.STATE_ROOT) -> None:
    root = _brain_root(state_root)
    root.mkdir(parents=True, exist_ok=True)
    _write(root / "README.md", "# Persona Brain\n\nLocal compiled view of Catalyst events, signals, memories, and sub-brains.\n")
    _write(root / "_index.md", "# Persona Brain Index\n\ncore: [[core/persona-summary]]\n\nsub-brains:\n" +
           "\n".join(f"- [[{name}/_index]]" for name in subbrains.SUBBRAIN_REGISTRY) + "\n")
    _write(root / "GRAPH.md", "# Persona Brain Graph\n\nMachine graph: `.catalyst/graph/graph.json`.\n")
    for name in subbrains.SUBBRAIN_REGISTRY:
        folder = root / name
        folder.mkdir(parents=True, exist_ok=True)
        _write(folder / "_index.md", f"# {name} index\n\nparent: [[../_index]]\ncore: [[../core/persona-summary]]\n")


def compile_subbrain(brain: str, nodes: list[dict], state_root: Path = store.STATE_ROOT) -> list[str]:
    root = _brain_root(state_root)
    mems = {m["id"]: m for m in memory.list_memories(limit=5000, state_root=state_root)}
    registry = subbrains.get_subbrain_registry()
    info = registry.get(brain, registry["core"])
    by_file: dict[str, list[dict]] = {}
    for node in nodes:
        if node.get("brain") == brain:
            by_file.setdefault(node.get("section") or info["default_file"], []).append(node)
    if not by_file:
        by_file[info["default_file"]] = []
    written = []
    for filename, owned in by_file.items():
        md_name = filename if filename.endswith(".md") else filename.replace(".jsonl", ".md")
        source_events, rows, maturities, confidences = [], [], [], []
        for node in owned:
            mem = mems.get(node.get("memory_id"), {})
            if not mem:
                continue
            source_events += mem.get("source_event_ids", [])
            maturities.append(float(mem.get("maturity", 1)))
            confidences.append(float(mem.get("confidence", 0.0)))
            rows.append(f"- {mem.get('text')} (memory `{mem.get('id')}`, confidence {mem.get('confidence')})")
        maturity = sum(maturities) / len(maturities) if maturities else 0.0
        confidence = sum(confidences) / len(confidences) if confidences else 0.0
        related = [b for b in subbrains.SUBBRAIN_REGISTRY if b != brain][:3]
        body = rows or ["- not enough signal yet"]
        text = (
            _frontmatter(brain, maturity, confidence, sorted(set(source_events))) +
            f"# {md_name[:-3]}\n\n"
            f"parent: {_wiki_link(brain + '/_index.md')}\n"
            "core: [[core/persona-summary]]\n\n"
            "related:\n" + "\n".join(f"- [[{r}/_index]]" for r in related) + "\n\n"
            + "source memories:\n" + "\n".join(body) + "\n\n"
            + "used_by:\n- [[agent-interface/agent-contract]]\n\n"
            + ("open questions:\n- needs more source signal\n" if not owned else "open questions:\n- none recorded\n")
        )
        written.append(_write(root / brain / md_name, text))
    return written


def compile_persona_brain(project: str | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    store.ensure_state(state_root)
    ensure_indexes(state_root)
    nodes = subbrains.list_persona_nodes(project, state_root)
    files = []
    for brain in subbrains.SUBBRAIN_REGISTRY:
        files.extend(compile_subbrain(brain, nodes, state_root))
    return {
        "ok": True,
        "root": str(_brain_root(state_root)),
        "files_compiled": len(files) + len(ROOT_FILES) + len(subbrains.SUBBRAIN_REGISTRY),
        "files": files,
        "orphans": find_orphan_files(state_root),
        "dead_links": find_dead_links(state_root),
    }


def find_orphan_files(state_root: Path = store.STATE_ROOT) -> list[str]:
    root = _brain_root(state_root)
    if not root.is_dir():
        return []
    orphans = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(root).as_posix()
        if path.name in ROOT_FILES or path.name == "_index.md":
            continue
        text = path.read_text(encoding="utf-8")
        if "parent:" not in text or "core:" not in text:
            orphans.append(rel)
    return orphans


def find_dead_links(state_root: Path = store.STATE_ROOT) -> list[str]:
    root = _brain_root(state_root)
    if not root.is_dir():
        return []
    dead = []
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for link in re.findall(r"\[\[([^\]]+)\]\]", text):
            target = (path.parent / (link + ".md")).resolve() if link.startswith("..") else (root / (link + ".md")).resolve()
            if not target.is_file():
                dead.append(f"{path.relative_to(root).as_posix()} -> {link}")
    return sorted(set(dead))
