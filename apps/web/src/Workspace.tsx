import React, { useEffect, useState } from "react";
import { api, Audit, Brain, BuildStatus, ConnectPrompts, EvalResult, Status } from "./api";
import { Button, Card, Field, ReadinessRing, Verdict } from "./components";
import BrainGraph from "./BrainGraph";

export default function Workspace() {
  const [status, setStatus] = useState<Status | null>(null);
  const [build, setBuild] = useState<BuildStatus | null>(null);
  const [connect, setConnect] = useState<ConnectPrompts | null>(null);
  const [name, setName] = useState("");
  const [brain, setBrain] = useState<Brain | null>(null);
  const [audit, setAudit] = useState<Audit | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [error, setError] = useState("");

  async function refresh() {
    try {
      const s = await api.status();
      setStatus(s);
      const active = s.active_brain || s.brains?.[0]?.name || "me";
      setName(active);
      setBuild(await api.buildStatus(active));
      api.connectPrompts().then(setConnect).catch(() => {});
      if (s.brains?.[0]?.name) {
        const realName = s.brains[0].name;
        api.brain(realName).then(setBrain).catch(() => setBrain(null));
        api.flowAudit(realName).then(setAudit).catch(() => setAudit(null));
      } else {
        setBrain(null);
        setAudit(null);
      }
      setError("");
    } catch (err: any) {
      setError(err?.message || "Could not refresh Catalyst status.");
    }
  }

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, []);

  async function openNode(file: string) {
    if (!status?.brains?.[0]?.name) return;
    setSelected(file);
    const r = await api.file(status.brains[0].name, `catalyst-brain/${file}`);
    setContent(r.content || r.error || "");
  }

  const activeBrain = status?.brains?.[0] || null;
  const missing = activeBrain?.brain_missing || [];
  const openQuestions = audit?.flags?.["open-questions.md"] || [];
  const readyScore = audit?.ready_score ?? 0;

  return (
    <div className="container wide stack">
      <div className="row spread wrap">
        <div>
          <div className="eyebrow">Command center</div>
          <h1 className="t" style={{ marginBottom: 0 }}>{activeBrain?.name || name || "your Catalyst Brain"}</h1>
          <p className="muted small" style={{ margin: "4px 0 0" }}>Identity, context, taste, judgment, and feedback memory for your agents.</p>
        </div>
        <div className="center"><ReadinessRing score={readyScore} size={56} /><div className="faint small">ready</div></div>
      </div>

      {error && <Card><p className="muted">{error}</p><Button onClick={refresh}>Retry</Button></Card>}

      <BuildTimeline status={build} />

      {!activeBrain && (
        <Card>
          <div className="eyebrow">Waiting</div>
          <h2 className="t">Waiting for your agent to build your Catalyst Brain.</h2>
          <p className="muted">
            Paste the setup prompt into Claude Code, Codex, Cursor, Hermes, or your MCP client.
            Catalyst will render progress when your agent writes <span className="mono">outputs/{name || "me"}/BUILD-STATUS.json</span>.
          </p>
          {connect?.clients?.[0] && <CopyButtonRow prompt={connect.clients[0].prompt} />}
        </Card>
      )}

      <div className="row wrap" style={{ alignItems: "stretch" }}>
        <Card className="grow" style={{ minWidth: 320, padding: "var(--s2)", overflow: "hidden" }}>
          <div className="row spread" style={{ padding: "var(--s2)" }}>
            <div>
              <div className="eyebrow">Brain graph</div>
              <p className="faint small" style={{ margin: 0 }}>A local section map, not a vector database.</p>
            </div>
            {activeBrain && <span className="chip">{activeBrain.brain_present.length} filled</span>}
          </div>
          <BrainGraph name={activeBrain?.name || name} brain={brain} audit={audit} selected={selected} onSelect={openNode} />
        </Card>
        <Card style={{ minWidth: 300, maxWidth: 400 }}>
          {selected ? (
            <>
              <div className="row spread">
                <div className="eyebrow">{selected.replace(".md", "")}</div>
                <Button variant="ghost" className="btn-sm" onClick={() => setSelected(null)}>Close</Button>
              </div>
              <div className="pre scroll" style={{ marginTop: "var(--s2)" }}>{content || "..."}</div>
            </>
          ) : (
            <ReadinessPanel missing={missing} openQuestions={openQuestions} audit={audit} />
          )}
        </Card>
      </div>

      <div className="grid-two">
        <AgentInstructions connect={connect} />
        <HostedCta />
      </div>

      <Card tight>
        <details>
          <summary className="eyebrow" style={{ cursor: "pointer" }}>Advanced: run the loop manually</summary>
          <div style={{ marginTop: "var(--s3)" }}>
            {activeBrain ? <LoopRunner name={activeBrain.name} onChanged={refresh} /> : <p className="muted small">No brain yet. Your agent builds it after you connect.</p>}
          </div>
        </details>
      </Card>
      <Card tight>
        <details>
          <summary className="eyebrow" style={{ cursor: "pointer" }}>Activity</summary>
          <div style={{ marginTop: "var(--s3)" }}>
            {activeBrain ? <Activity name={activeBrain.name} /> : <p className="muted small">No feedback captured yet.</p>}
          </div>
        </details>
      </Card>
    </div>
  );
}

function BuildTimeline({ status }: { status: BuildStatus | null }) {
  if (!status) return <Card><p className="muted">Loading build status...</p></Card>;
  return (
    <Card>
      <div className="row spread wrap">
        <div>
          <div className="eyebrow">Build status</div>
          <h2 className="t" style={{ marginBottom: 0 }}>{status.status === "waiting" ? "Agent build not started yet" : status.step.replace(/_/g, " ")}</h2>
        </div>
        <span className={`badge ${status.status === "ready" ? "ship" : status.status === "error" ? "reject" : "ask"}`}><span className="dot" />{status.status}</span>
      </div>
      <div className="progress"><span style={{ width: `${Math.round(status.progress * 100)}%` }} /></div>
      <p className="muted small">{status.message}</p>
      <div className="timeline">
        {status.steps.map((step) => (
          <div key={step.id} className={`timeline-step ${step.state}`}>
            <span className="marker" />
            <span>{step.label}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

function ReadinessPanel({ missing, openQuestions, audit }: { missing: string[]; openQuestions: string[]; audit: Audit | null }) {
  return (
    <div>
      <div className="eyebrow">Readiness</div>
      <p className="muted small">{audit?.summary || "No completed brain audit yet."}</p>
      <div className="group-label">Missing context</div>
      {missing.length === 0 ? <p className="faint small">No missing files reported.</p> : (
        <ul className="muted small">{missing.slice(0, 8).map((m) => <li key={m}>{m}</li>)}</ul>
      )}
      <div className="group-label">Open questions</div>
      {openQuestions.length === 0 ? <p className="faint small">No open question flags yet.</p> : (
        <ul className="muted small">{openQuestions.map((q) => <li key={q}>{q}</li>)}</ul>
      )}
    </div>
  );
}

function CopyButtonRow({ prompt }: { prompt: string }) {
  return (
    <div className="row wrap">
      <Button variant="primary" onClick={async () => navigator.clipboard.writeText(prompt)}>Copy setup prompt</Button>
      <span className="faint small">Paste it into your agent. The dashboard only watches local files.</span>
    </div>
  );
}

function AgentInstructions({ connect }: { connect: ConnectPrompts | null }) {
  const first = connect?.clients?.[0];
  return (
    <Card>
      <div className="eyebrow">Connected-agent instructions</div>
      <h2 className="t">Use the same brain from every local agent.</h2>
      <p className="muted small">Claude Code, Codex, Cursor, Hermes, and manual MCP all get copyable instructions. These are instructions, not fake OAuth connectors.</p>
      {first?.command && <div className="pre">{first.command}</div>}
      {first && <div style={{ marginTop: "var(--s2)" }}><Button onClick={async () => navigator.clipboard.writeText(first.prompt)}>Copy prompt</Button></div>}
    </Card>
  );
}

function HostedCta() {
  return (
    <Card>
      <div className="eyebrow">Hosted Catalyst</div>
      <h2 className="t">Want this synced across every agent without local setup?</h2>
      <p className="muted small">Join hosted Catalyst, or book a founding install and get this set up for you.</p>
      <div className="row wrap">
        <a className="btn btn-primary" href="https://itscatalyst.com">Join hosted Catalyst</a>
        <a className="btn" href="mailto:hello@itscatalyst.com?subject=Founding%20Catalyst%20install">Book founding install</a>
      </div>
    </Card>
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
      <p className="muted small" style={{ marginTop: 0 }}>Manual access to the same local judgment loop your agent uses over MCP.</p>
      <Field label="Task" placeholder="e.g. write a DM reply about Catalyst" value={task} onChange={(e: any) => setTask(e.target.value)} />
      <Button className="btn-sm" disabled={!task || busy === "context"} onClick={context}>{busy === "context" ? "Building..." : "Build context"}</Button>
      {packet && <div className="pre scroll" style={{ marginTop: "var(--s2)" }}>{packet}</div>}

      <div className="divider" />
      <Field label="Draft output to evaluate" textarea placeholder="Paste a draft to judge against your standards..." value={draft} onChange={(e: any) => setDraft(e.target.value)} />
      <Button className="btn-sm" disabled={!task || !draft || busy === "eval"} onClick={evaluate}>{busy === "eval" ? "Evaluating..." : "Evaluate"}</Button>
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
      <Field label="Correct it (captured as a proposal - never silently applied)" placeholder="e.g. too pitchy, sound more human" value={fb} onChange={(e: any) => setFb(e.target.value)} />
      <Button className="btn-sm" disabled={!task || !fb || busy === "fb"} onClick={feedback}>{busy === "fb" ? "Capturing..." : "Capture feedback"}</Button>
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
      {entries.length === 0 && <p className="muted small" style={{ marginTop: 0 }}>No feedback captured yet. Correct an output through your agent or the advanced loop.</p>}
      {entries.slice(-6).reverse().map((e, i) => (
        <div key={i} className="pre" style={{ marginTop: "var(--s2)" }}>{e.trim().slice(0, 600)}</div>
      ))}
    </div>
  );
}
