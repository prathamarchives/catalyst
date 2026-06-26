"""Machine-readable graph for events, signals, memories, nodes, and brain files."""
from __future__ import annotations

from pathlib import Path

from . import events, memory, signals, store, subbrains


def build_graph(project: str | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    evs = events.list_events(project, limit=10000, state_root=state_root)
    sigs = signals.list_signals(project, limit=10000, state_root=state_root)
    mems = memory.list_memories(project, limit=10000, state_root=state_root)
    nodes = subbrains.list_persona_nodes(project, state_root)
    graph_nodes, edges = [], []
    for e in evs:
        graph_nodes.append({"id": e["id"], "kind": "event", "label": e.get("type")})
    for s in sigs:
        graph_nodes.append({"id": s["id"], "kind": "signal", "label": s.get("type")})
        edges.append({"from": s.get("source_event_id"), "to": s["id"], "relation": "derived_from", "note": "", "created_at": s.get("created_at")})
    for m in mems:
        graph_nodes.append({"id": m["id"], "kind": "memory", "label": m.get("type")})
        for sid in m.get("source_signal_ids", []):
            edges.append({"from": sid, "to": m["id"], "relation": "updates", "note": "signal became memory", "created_at": m.get("updated_at")})
    for n in nodes:
        graph_nodes.append({"id": n["id"], "kind": "persona_node", "label": n.get("brain")})
        edges.append({"from": n.get("memory_id"), "to": n["id"], "relation": "routes_to", "note": n.get("section", ""), "created_at": n.get("created_at")})
        graph_nodes.append({"id": f"brain:{n.get('brain')}", "kind": "sub_brain", "label": n.get("brain")})
        edges.append({"from": n["id"], "to": f"brain:{n.get('brain')}", "relation": "used_by", "note": n.get("section", ""), "created_at": n.get("created_at")})
    return {"project": project or "all", "nodes": graph_nodes, "edges": edges, "created_at": store.now_iso()}


def save_graph(graph: dict, state_root: Path = store.STATE_ROOT) -> dict:
    return store.write_json("graph/graph.json", graph, state_root)


def load_graph(state_root: Path = store.STATE_ROOT) -> dict:
    return store.read_json("graph/graph.json", {"nodes": [], "edges": []}, state_root)


def graph_summary(project: str | None = None, state_root: Path = store.STATE_ROOT) -> dict:
    g = load_graph(state_root)
    if not g.get("nodes"):
        g = build_graph(project, state_root)
    return {
        "project": project or g.get("project") or "all",
        "nodes": len(g.get("nodes", [])),
        "edges": len(g.get("edges", [])),
        "node_kinds": sorted(set(n.get("kind") for n in g.get("nodes", []))),
    }

