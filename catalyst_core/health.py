"""System health for the local Persona Brain runtime."""
from __future__ import annotations

from pathlib import Path

from . import compiler, events, graph, memory, signals, store, subbrains, traces


def get_health(project: str | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    store.ensure_state(state_root)
    evs = events.list_events(project, limit=10000, state_root=state_root)
    sigs = signals.list_signals(project, limit=10000, state_root=state_root)
    mems = memory.list_memories(project, limit=10000, state_root=state_root)
    g = graph.load_graph(state_root)
    recalls = store.read_jsonl("logs/recall.jsonl", state_root)
    reviews = store.read_jsonl("logs/reviews.jsonl", state_root)
    trace_rows = traces.list_traces(project, limit=10000, state_root=state_root)
    health = {
        "ok": True,
        "project": project or "all",
        "state_root": str(Path(state_root)),
        "events_count": len(evs),
        "signals_count": len(sigs),
        "memories_count": len(mems),
        "subbrain_maturity": subbrains.get_subbrain_status(project, state_root),
        "graph": graph.graph_summary(project, state_root),
        "graph_node_count": len(g.get("nodes", [])),
        "graph_edge_count": len(g.get("edges", [])),
        "orphan_files": compiler.find_orphan_files(state_root),
        "dead_links": compiler.find_dead_links(state_root),
        "missing_indexes": _missing_indexes(state_root),
        "recall_count": len(recalls),
        "capture_count": len(evs),
        "review_count": len(reviews),
        "trace_count": len(trace_rows),
        "last_compile": store.read_json("logs/last_compile.json", {}, state_root).get("created_at"),
        "warnings": [],
        "created_at": store.now_iso(),
    }
    if not mems:
        health["warnings"].append("no memories captured yet")
    if health["dead_links"]:
        health["warnings"].append("dead wiki links present")
    store.write_json("logs/health.json", health, state_root)
    return health


def _missing_indexes(state_root: Path) -> list[str]:
    root = store.state_path("persona-brain", state_root=state_root)
    missing = []
    if not (root / "_index.md").is_file():
        missing.append("_index.md")
    for brain in subbrains.SUBBRAIN_REGISTRY:
        if not (root / brain / "_index.md").is_file():
            missing.append(f"{brain}/_index.md")
    return missing

