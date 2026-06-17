import React, { useEffect, useRef, useState } from "react";
import { forceSimulation, forceManyBody, forceLink, forceCenter, forceCollide } from "d3-force";
import { Audit, Brain } from "./api";

type Node = {
  id: string;
  kind: "center" | "group" | "file";
  label: string;
  file?: string;
  filled?: boolean;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
};
type Link = { source: any; target: any; kind: string };

const W = 760;
const H = 480;

function buildGraph(name: string, brain: Brain | null, placeholders: Set<string>) {
  const nodes: Node[] = [{ id: "__center__", kind: "center", label: name || "you" }];
  const links: Link[] = [];
  if (brain) {
    for (const g of brain.groups) {
      const gid = "g:" + g.label;
      nodes.push({ id: gid, kind: "group", label: g.label });
      links.push({ source: "__center__", target: gid, kind: "cg" });
      for (const f of g.files) {
        const fid = "f:" + f.file;
        nodes.push({ id: fid, kind: "file", label: f.file.replace(".md", ""), file: f.file, filled: !placeholders.has(f.file) });
        links.push({ source: gid, target: fid, kind: "gf" });
      }
    }
  }
  return { nodes, links };
}

export default function BrainGraph({ name, brain, audit, selected, onSelect }: {
  name: string;
  brain: Brain | null;
  audit: Audit | null;
  selected: string | null;
  onSelect: (file: string) => void;
}) {
  const placeholders = new Set(
    Object.entries(audit?.flags || {}).filter(([, v]) => v.some((x) => x.includes("placeholder"))).map(([k]) => k),
  );
  const svgRef = useRef<SVGSVGElement | null>(null);
  const simRef = useRef<any>(null);
  const nodesRef = useRef<Node[]>([]);
  const linksRef = useRef<Link[]>([]);
  const dragId = useRef<string | null>(null);
  const [, tick] = useState(0);

  // rebuild only when the node set or fill state (or name) changes
  const sig = name + "::" + (brain?.groups || [])
    .map((g) => g.files.map((f) => f.file + (placeholders.has(f.file) ? "0" : "1")).join(",")).join("|");

  useEffect(() => {
    const { nodes, links } = buildGraph(name, brain, placeholders);
    const prev = new Map(nodesRef.current.map((n) => [n.id, n]));
    for (const n of nodes) {
      const p = prev.get(n.id);
      if (p) { n.x = p.x; n.y = p.y; }
    }
    nodesRef.current = nodes;
    linksRef.current = links;
    simRef.current?.stop();
    const sim = forceSimulation(nodes as any)
      .force("charge", forceManyBody().strength(-260))
      .force("link", forceLink(links as any).id((d: any) => d.id).distance((l: any) => (l.kind === "cg" ? 92 : 58)).strength(0.5))
      .force("center", forceCenter(W / 2, H / 2))
      .force("collide", forceCollide().radius((d: any) => (d.kind === "center" ? 36 : d.kind === "group" ? 26 : 18)))
      .on("tick", () => tick((t) => t + 1));
    sim.alpha(1).restart();
    simRef.current = sim;
    return () => sim.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sig]);

  function toSvg(e: React.PointerEvent) {
    const svg = svgRef.current;
    if (!svg) return { x: 0, y: 0 };
    const pt = svg.createSVGPoint();
    pt.x = e.clientX; pt.y = e.clientY;
    const m = svg.getScreenCTM();
    if (!m) return { x: 0, y: 0 };
    const p = pt.matrixTransform(m.inverse());
    return { x: p.x, y: p.y };
  }
  function onDown(id: string, e: React.PointerEvent) {
    dragId.current = id;
    (e.target as Element).setPointerCapture?.(e.pointerId);
    simRef.current?.alphaTarget(0.25).restart();
  }
  function onMove(e: React.PointerEvent) {
    if (!dragId.current) return;
    const { x, y } = toSvg(e);
    const n = nodesRef.current.find((m) => m.id === dragId.current);
    if (n) { n.fx = x; n.fy = y; }
  }
  function onUp() {
    const n = nodesRef.current.find((m) => m.id === dragId.current);
    if (n) { n.fx = null; n.fy = null; }
    dragId.current = null;
    simRef.current?.alphaTarget(0);
  }

  const nodes = nodesRef.current;
  const links = linksRef.current;

  return (
    <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} width="100%" style={{ display: "block", touchAction: "none" }}
      onPointerMove={onMove} onPointerUp={onUp} onPointerLeave={onUp}>
      {links.map((l, i) => {
        const s = (typeof l.source === "object" ? l.source : null) as Node | null;
        const t = (typeof l.target === "object" ? l.target : null) as Node | null;
        if (!s || !t) return null;
        return <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="var(--line-strong)" strokeWidth={1} opacity={0.65} />;
      })}
      {nodes.map((n) => {
        const r = n.kind === "center" ? 22 : n.kind === "group" ? 13 : 9;
        const isFile = n.kind === "file";
        const hollow = isFile && !n.filled;
        const sel = isFile && selected === n.file;
        const fill = n.kind === "center" ? "var(--ink)" : hollow ? "var(--surface)" : isFile ? "var(--ink)" : "var(--surface)";
        return (
          <g key={n.id} transform={`translate(${n.x ?? W / 2},${n.y ?? H / 2})`}
            style={{ cursor: isFile ? "pointer" : "grab" }}
            onPointerDown={(e) => onDown(n.id, e)}
            onClick={() => isFile && onSelect(n.file!)}>
            <circle r={r} fill={fill}
              stroke={sel ? "var(--ink)" : hollow ? "var(--line-strong)" : "var(--ink)"}
              strokeWidth={sel ? 3 : n.kind === "group" ? 2 : 1.5}
              strokeDasharray={hollow ? "3 3" : undefined} />
            <text textAnchor="middle" y={r + 13} fontSize={n.kind === "center" ? 13 : 11}
              fill={hollow ? "var(--ink-faint)" : "var(--ink-soft)"}
              style={{ fontWeight: n.kind === "center" ? 600 : 400, pointerEvents: "none", userSelect: "none" }}>
              {n.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
