import React, { useEffect, useState } from "react";
import { api, Audit, Brain, EvalResult } from "./api";
import { Button, Card, Field, ReadinessRing, Verdict } from "./components";
import BrainGraph from "./BrainGraph";

// The dashboard: your brain as a living graph. Self-resolves the active brain from
// /api/status and polls, so nodes appear and solidify as the agent builds it.
export default function Workspace() {
  const [name, setName] = useState("");
  const [brain, setBrain] = useState<Brain | null>(null);
  const [audit, setAudit] = useState<Audit | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState("");

  async function refresh() {
    const s = await api.status().catch(() => null);
    const first = s?.brains?.[0]?.name || "";
    setName(first);
    if (first) {
      api.brain(first).then(setBrain).catch(() => {});
      api.flowAudit(first).then(setAudit).catch(() => {});
    } else {
      setBrain(null);
      setAudit(null);
    }
  }
  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, []);

  async function openNode(file: string) {
    setSelected(file);
    const r = await api.file(name, `catalyst-brain/${file}`);
    setContent(r.content || r.error || "");
  }

  return (
    <div className="container wide stack">
      <div className="row spread">
        <div>
          <div className="eyebrow">Workspace</div>
          <h1 className="t" style={{ marginBottom: 0 }}>{name || "your brain"}</h1>
        </div>
        {audit && <div className="center"><ReadinessRing score={audit.ready_score} size={56} /><div className="faint small">ready</div></div>}
      </div>

      {!name && (
        <Card className="center">
          <p className="muted" style={{ marginBottom: 6 }}>Connected — your agent is building your brain. Nodes appear here as it works.</p>
          <p className="faint small" style={{ margin: 0 }}>
            Give your agent a task, or run the <span className="mono">catalyst-build-and-run</span> prompt. This refreshes automatically.
          </p>
        </Card>
      )}

      <div className="row wrap" style={{ alignItems: "stretch" }}>
        <Card className="grow" style={{ minWidth: 320, padding: "var(--s2)", overflow: "hidden" }}>
          <BrainGraph name={name} brain={brain} audit={audit} selected={selected} onSelect={openNode} />
        </Card>
        {selected && (
          <Card style={{ minWidth: 300, maxWidth: 400 }}>
            <div className="row spread">
              <div className="eyebrow">{selected.replace(".md", "")}</div>
              <Button variant="ghost" className="btn-sm" onClick={() => setSelected(null)}>Close</Button>
            </div>
            <div className="pre scroll" style={{ marginTop: "var(--s2)" }}>{content || "…"}</div>
          </Card>
        )}
      </div>

      <Card tight>
        <details>
          <summary className="eyebrow" style={{ cursor: "pointer" }}>Run the loop</summary>
          <div style={{ marginTop: "var(--s3)" }}>
            {name ? <LoopRunner name={name} onChanged={refresh} /> : <p className="muted small">No brain yet — your agent builds it after you connect.</p>}
          </div>
        </details>
      </Card>
      <Card tight>
        <details>
          <summary className="eyebrow" style={{ cursor: "pointer" }}>Activity</summary>
          <div style={{ marginTop: "var(--s3)" }}>
            {name ? <Activity name={name} /> : <p className="muted small">No activity yet.</p>}
          </div>
        </details>
      </Card>
    </div>
  );
}

function LoopRunner({ name, onChanged }: { name: string; onChanged: () => void }) {
  const [task, setTask] = useState("");
  const [packet, setPacket] = useState("");
  const [draft, setDraft] = useState("");
  const [report, setReport] = useState<EvalResult | null>(null);
  const [fb, setFb] = useState("");
  const [logged, setLogged] = useState<string[] | null>(null);
  const [busy, setBusy] = useState("");

  async function context() { setBusy("context"); setPacket((await api.flowContext(name, task)).packet || ""); setBusy(""); }
  async function evaluate() { setBusy("eval"); setReport(await api.flowEvaluate(name, task, draft)); setBusy(""); }
  async function feedback() {
    setBusy("fb");
    const r = await api.flowFeedback(name, task, draft, fb);
    setLogged(r.written || [r.error]);
    setFb(""); onChanged(); setBusy("");
  }

  return (
    <div>
      <p className="muted small" style={{ marginTop: 0 }}>Try the judgment loop yourself — the same calls your agent makes over MCP.</p>
      <Field label="Task" placeholder="e.g. write a DM reply about Catalyst" value={task} onChange={(e: any) => setTask(e.target.value)} />
      <Button className="btn-sm" disabled={!task || busy === "context"} onClick={context}>{busy === "context" ? "…" : "Build context"}</Button>
      {packet && <div className="pre scroll" style={{ marginTop: "var(--s2)" }}>{packet}</div>}

      <div className="divider" />
      <Field label="Draft output to evaluate" textarea placeholder="Paste a draft to judge against your standards…" value={draft} onChange={(e: any) => setDraft(e.target.value)} />
      <Button className="btn-sm" disabled={!task || !draft || busy === "eval"} onClick={evaluate}>{busy === "eval" ? "…" : "Evaluate"}</Button>
      {report && (
        <div style={{ marginTop: "var(--s2)" }}>
          <div className="row wrap">
            <Verdict value={report.verdict} />
            {Object.entries(report.scores).map(([k, v]) => <span key={k} className="chip">{k.replace(/_/g, " ")}: {v}/5</span>)}
          </div>
          {report.issues.length > 0 && <ul className="muted small">{report.issues.map((i, n) => <li key={n}>{i}</li>)}</ul>}
        </div>
      )}

      <div className="divider" />
      <Field label="Correct it (captured as a proposal — never silently applied)" placeholder="e.g. too pitchy, sound more human" value={fb} onChange={(e: any) => setFb(e.target.value)} />
      <Button className="btn-sm" disabled={!task || !fb || busy === "fb"} onClick={feedback}>{busy === "fb" ? "…" : "Capture feedback"}</Button>
      {logged && <p className="small muted" style={{ marginTop: "var(--s2)" }}>Wrote: {logged.join(", ")}</p>}
    </div>
  );
}

function Activity({ name }: { name: string }) {
  const [log, setLog] = useState("");
  useEffect(() => {
    api.file(name, "evals/improvement-log.md").then((r) => setLog(r.content || "")).catch(() => {});
  }, [name]);
  const entries = log.split("## entry").slice(1);
  return (
    <div>
      {entries.length === 0 && <p className="muted small" style={{ marginTop: 0 }}>No feedback captured yet. Correct an output (here or via your agent) and it lands here and as a proposal.</p>}
      {entries.slice(-6).reverse().map((e, i) => (
        <div key={i} className="pre" style={{ marginTop: "var(--s2)" }}>{e.trim().slice(0, 600)}</div>
      ))}
    </div>
  );
}
