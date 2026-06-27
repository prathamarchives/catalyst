"""Local JSON index helpers for Catalyst runtime state."""
from __future__ import annotations

from pathlib import Path

from . import brain_manager, graph, memory, store


def build_index(project: str | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    profile = brain_manager.load_brain_profile(project or "default")
    mems = memory.list_memories(project=project, limit=1000, state_root=state_root)
    g = graph.load_graph(state_root)
    data = {
        "project": project or "default",
        "brain_sections": [s.name for s in profile.sections.values() if s.status != "missing"],
        "memory_atoms": len(mems),
        "memory_targets": sorted(set(m.get("target_brain") for m in mems if m.get("target_brain"))),
        "graph_nodes": len(g.get("nodes", [])),
        "graph_edges": len(g.get("edges", [])),
        "updated_at": store.now_iso(),
    }
    store.write_json("index/index.json", data, state_root)
    return data


def read_index(state_root: Path = store.STATE_ROOT) -> dict:
    return store.read_json("index/index.json", {"brain_sections": [], "memory_atoms": 0}, state_root)

