import React, { useEffect, useState } from "react";
import { api, Audit, Brain, EvalResult } from "./api";
import { Button, Card, Field, ReadinessRing, SectionView, Verdict } from "./components";

export default function Workspace({ name }: { name: string }) {
  const [brain, setBrain] = useState<Brain | null>(null);
  const [audit, setAudit] = useState<Audit | null>(null);

  const refreshAudit = () => api.flowAudit(name).then(setAudit).catch(() => {});
  useEffect(() => {
    if (!name) return;
    api.brain(name).then(setBrain).catch(() => {});
    refreshAudit();
  }, [name]);

  const placeholders = new Set(Object.entries(audit?.flags || {})
    .filter(([, v]) => v.some((x) => x.includes("placeholder"))).map(([k]) => k));

  return (
    <div className="container wide stack">
      <div className="row spread">
        <div>
          <div className="eyebrow">Workspace</div>
          <h1 className="t" style={{ marginBottom: 0 }}>{name}</h1>
        </div>
        {audit && <div className="center"><ReadinessRing score={audit.ready_score} size={56} /><div className="faint small">ready</div></div>}
      </div>

      <LoopRunner name={name} onChanged={refreshAudit} />

      <div className="row wrap" style={{ alignItems: "flex-start" }}>
        <Card className="grow" style={{ minWidth: 280 }}>
          <div className="eyebrow">Brain</div>
          {!brain && <p className="muted small">Loading…</p>}
          {brain?.groups.map((g) => (
            <div key={g.label}>
              <div className="group-label">{g.label}</div>
              {g.files.map((f) => (
                <BrainRow key={f.file} name={name} file={f.file} filled={!placeholders.has(f.file)} />
              ))}
            </div>
          ))}
        </Card>
        <Activity name={name} className="grow" />
      </div>
    </div>
  );
}

function BrainRow({ name, file, filled }: { name: string; file: string; filled: boolean }) {
  const [open, setOpen] = useState(false);
  const [content, setContent] = useState("");
  async function toggle() {
    if (!open && !content) {
      const r = await api.file(name, `catalyst-brain/${file}`);
      setContent(r.content || r.error || "");
    }
    setOpen(!open);
  }
  return (
    <div onClick={toggle} style={{ cursor: "pointer" }}>
      <SectionView name={file.replace(".md", "")} filled={filled} body={open ? content : undefined} />
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
    <Card>
      <div className="eyebrow">Run the loop</div>
      <p className="muted small">Try the judgment loop yourself — the same calls your agent makes over MCP.</p>
      <Field label="Task" placeholder="e.g. write a DM reply about Catalyst" value={task} onChange={(e: any) => setTask(e.target.value)} />
      <div className="row wrap">
        <Button className="btn-sm" disabled={!task || busy === "context"} onClick={context}>{busy === "context" ? "…" : "Build context"}</Button>
      </div>
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
          {report.missing_context_questions.length > 0 && <ul className="small" style={{ color: "var(--info)" }}>{report.missing_context_questions.map((i, n) => <li key={n}>{i}</li>)}</ul>}
        </div>
      )}

      <div className="divider" />
      <Field label="Correct it (captured as a proposal — never silently applied)" placeholder="e.g. too pitchy, sound more human" value={fb} onChange={(e: any) => setFb(e.target.value)} />
      <Button className="btn-sm" disabled={!task || !fb || busy === "fb"} onClick={feedback}>{busy === "fb" ? "…" : "Capture feedback"}</Button>
      {logged && <p className="small muted" style={{ marginTop: "var(--s2)" }}>Wrote: {logged.join(", ")}</p>}
    </Card>
  );
}

function Activity({ name, className = "" }: { name: string; className?: string }) {
  const [log, setLog] = useState("");
  useEffect(() => {
    api.file(name, "evals/improvement-log.md").then((r) => setLog(r.content || "")).catch(() => {});
  }, [name]);
  const entries = log.split("## entry").slice(1);
  return (
    <Card className={className} style={{ minWidth: 280 }}>
      <div className="eyebrow">Activity</div>
      {entries.length === 0 && <p className="muted small">No feedback captured yet. Run the loop and correct an output — it lands here and as a proposal.</p>}
      {entries.slice(-6).reverse().map((e, i) => (
        <div key={i} className="pre" style={{ marginTop: "var(--s2)" }}>{e.trim().slice(0, 600)}</div>
      ))}
    </Card>
  );
}
