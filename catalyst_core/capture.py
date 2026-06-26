"""One-call capture pipeline: event -> signal -> memory -> sub-brain -> graph -> wiki."""
from __future__ import annotations

from pathlib import Path

from . import compiler, events, graph, health, memory, signals, store, subbrains, traces


def capture_event(event: dict, state_root: Path = store.STATE_ROOT) -> dict:
    store.ensure_state(state_root)
    ev = events.append_event(event, state_root)
    extracted = signals.extract_signals(ev)
    signals.append_signals(extracted, state_root)
    memories, nodes = [], []
    for sig in extracted:
        mem = memory.create_or_merge_memory(sig, state_root)
        memories.append(mem)
        routed = subbrains.route_memory(mem)
        nodes.extend(routed)
        subbrains.append_persona_nodes(routed, state_root)
    g = graph.build_graph(ev.get("project"), state_root)
    graph.save_graph(g, state_root)
    compiled = compiler.compile_persona_brain(ev.get("project"), state_root)
    store.write_json("logs/last_compile.json", {"created_at": store.now_iso(), **compiled}, state_root)
    health_summary = health.get_health(ev.get("project"), state_root)
    trace = traces.append_trace({
        "agent": ev.get("agent"),
        "project": ev.get("project"),
        "task": ev.get("task"),
        "output_summary": (ev.get("output") or "")[:240],
        "capture_event_id": ev["id"],
        "memory_updates": [m["id"] for m in memories],
    }, state_root)
    return {
        "ok": True,
        "event_id": ev["id"],
        "signals_created": len(extracted),
        "signal_ids": [s["id"] for s in extracted],
        "memories_created_or_updated": len(memories),
        "memory_ids": [m["id"] for m in memories],
        "sub_brains_affected": sorted(set(n["brain"] for n in nodes)),
        "graph_updated": True,
        "files_compiled": compiled.get("files_compiled", 0),
        "health_summary": {
            "events": health_summary["events_count"],
            "signals": health_summary["signals_count"],
            "memories": health_summary["memories_count"],
            "warnings": health_summary["warnings"],
        },
        "trace_id": trace["id"],
    }

