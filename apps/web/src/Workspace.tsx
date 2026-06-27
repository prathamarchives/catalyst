import React, { useEffect, useMemo, useState } from "react";
import {
  api,
  Audit,
  Brain,
  BrainContextPacket,
  BuildStatus,
  ConnectPrompts,
  HybridEvalResult,
  Proposal,
  RuntimeEvent,
  Status,
} from "./api";
import { Button, Card, CatalystMark, CopyButton, Field, ReadinessRing, Verdict } from "./components";
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
    try {
      const r = await api.file(status.brains[0].name, `catalyst-brain/${file}`);
      setContent(r.content || r.error || "");
    } catch (err: any) {
      setContent(err?.message || "Could not load this brain file.");
    }
  }

  const activeBrain = status?.brains?.[0] || null;
  const missing = activeBrain?.brain_missing || [];
  const openQuestions = audit?.flags?.["open-questions.md"] || [];
  const readyScore = audit?.ready_score ?? 0;
  const captures = status?.recent_captures || [];
  const firstClient = connect?.clients?.[0] || null;

  return (
    <main className="workspace-page">
      <section className="workspace-hero reveal is-visible">
        <div className="workspace-title">
          <div className="brand-kicker">
            <CatalystMark />
            <span>Private local command center</span>
          </div>
          <h1>{activeBrain?.name || name || "Catalyst Brain"}</h1>
          <p>
            Inspect identity, context, taste, judgment, graph health, MCP access, feedback, evals,
            and proposals without pretending the browser is the agent.
          </p>
        </div>
        <div className="readiness-orb glass-card">
          <ReadinessRing score={readyScore} size={78} />
          <strong>{activeBrain ? "Brain readiness" : "No brain yet"}</strong>
          <span>{audit?.summary || "Waiting for a completed local audit."}</span>
        </div>
      </section>

      <section className="container command-shell">
        {error && (
          <Card className="error-card">
            <p className="muted">{error}</p>
            <Button onClick={refresh}>Retry</Button>
          </Card>
        )}

        <RuntimeLanes status={status} connect={connect} activeBrain={activeBrain} audit={audit} />
        <BuildTimeline status={build} />

        {!activeBrain && <EmptyBrainPanel name={name} connect={connect} />}

        <div className="command-grid">
          <Card className="brain-map-card">
            <div className="row spread wrap card-head">
              <div>
                <p className="eyebrow">Brain graph</p>
                <h2 className="t">Local brain map</h2>
                <p className="faint small">A visual map of the files agents use, not a vector index.</p>
              </div>
              {activeBrain && <span className="chip">{activeBrain.brain_present.length} filled</span>}
            </div>
            <BrainGraph name={activeBrain?.name || name} brain={brain} audit={audit} selected={selected} onSelect={openNode} />
          </Card>

          <Card className="inspector-card">
            {selected ? (
              <>
                <div className="row spread">
                  <div>
                    <p className="eyebrow">Brain file</p>
                    <h2 className="t">{selected.replace(".md", "")}</h2>
                  </div>
                  <Button variant="ghost" className="btn-sm" onClick={() => setSelected(null)}>Close</Button>
                </div>
                <div className="pre scroll">{content || "Loading file..."}</div>
              </>
            ) : (
              <ReadinessPanel missing={missing} openQuestions={openQuestions} audit={audit} />
            )}
          </Card>
        </div>

        <div className="grid-two">
          <AgentInstructions connect={connect} />
          <SystemHealth status={status} captures={captures} />
        </div>

        <div className="grid-two">
          <FeedbackPanel activeBrain={activeBrain} name={activeBrain?.name || name} onChanged={refresh} />
          <OssPathCard firstClient={firstClient} />
        </div>
      </section>
    </main>
  );
}

function RuntimeLanes({ status, connect, activeBrain, audit }: {
  status: Status | null;
  connect: ConnectPrompts | null;
  activeBrain: Status["brains"][number] | null;
  audit: Audit | null;
}) {
  const lanes = [
    {
      label: "Local brain",
      value: activeBrain ? `${activeBrain.brain_present.length} sections filled` : "waiting",
      state: activeBrain ? "ship" : "ask",
    },
    {
      label: "MCP clients",
      value: connect ? `${connect.clients.length} available` : "loading",
      state: connect ? "ship" : "ask",
    },
    {
      label: "Permission",
      value: status?.permissions?.label || "not selected",
      state: status?.permissions?.mode && status.permissions.mode !== "unset" ? "ship" : "ask",
    },
    {
      label: "Eval audit",
      value: audit ? `${Math.round((audit.ready_score || 0) * 100)} ready` : "not run",
      state: audit ? "ship" : "ask",
    },
  ];

  return (
    <div className="runtime-lanes reveal">
      {lanes.map((lane) => (
        <div className="runtime-lane glass-card" key={lane.label}>
          <span className={`badge ${lane.state}`}><span className="dot" />{lane.label}</span>
          <strong>{lane.value}</strong>
        </div>
      ))}
    </div>
  );
}

function EmptyBrainPanel({ name, connect }: { name: string; connect: ConnectPrompts | null }) {
  const first = connect?.clients?.[0];
  const config = first ? JSON.stringify(first.mcp_config, null, 2) : "";
  return (
    <Card className="empty-state">
      <div>
        <p className="eyebrow">Waiting for agent</p>
        <h2 className="t">No local Catalyst Brain has been built yet.</h2>
        <p className="muted">
          Add the MCP server to your agent, approve scan scope, then let the agent write
          <span className="mono"> outputs/{name || "me"}/BUILD-STATUS.json</span> and the generated brain.
        </p>
      </div>
      <div className="empty-actions">
        {config && <CopyButton text={config} label="Copy MCP JSON" variant="primary" />}
        {first?.prompt && <CopyButton text={first.prompt} label="Copy setup prompt" />}
      </div>
    </Card>
  );
}

function BuildTimeline({ status }: { status: BuildStatus | null }) {
  if (!status) return <Card><p className="muted">Loading build status from the local runtime...</p></Card>;
  return (
    <Card className="build-card reveal">
      <div className="row spread wrap">
        <div>
          <p className="eyebrow">Build status</p>
          <h2 className="t">{status.status === "waiting" ? "Agent build not started yet" : status.step.replace(/_/g, " ")}</h2>
        </div>
        <span className={`badge ${status.status === "ready" ? "ship" : status.status === "error" ? "reject" : "ask"}`}>
          <span className="dot" />
          {status.status}
        </span>
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
    <div className="readiness-panel">
      <p className="eyebrow">Readiness</p>
      <h2 className="t">What the agent still needs</h2>
      <p className="muted small">{audit?.summary || "No completed brain audit yet."}</p>
      <div className="group-label">Missing context</div>
      {missing.length === 0 ? <p className="faint small">No missing brain files reported.</p> : (
        <ul className="muted small">{missing.slice(0, 8).map((m) => <li key={m}>{m}</li>)}</ul>
      )}
      <div className="group-label">Open questions</div>
      {openQuestions.length === 0 ? <p className="faint small">No open question flags yet.</p> : (
        <ul className="muted small">{openQuestions.map((q) => <li key={q}>{q}</li>)}</ul>
      )}
    </div>
  );
}

function AgentInstructions({ connect }: { connect: ConnectPrompts | null }) {
  const first = connect?.clients?.[0];
  const manual = connect?.clients?.find((client) => client.id === "manual-mcp") || first;
  const config = manual ? JSON.stringify(manual.mcp_config, null, 2) : "";
  return (
    <Card>
      <p className="eyebrow">MCP-first agent connection</p>
      <h2 className="t">Use the same brain from every local agent.</h2>
      <p className="muted small">
        Claude Code, Codex, Cursor, Hermes, and manual MCP receive the same local server config.
        The giant prompt is now a fallback, not the center of the product.
      </p>
      {config ? (
        <>
          <div className="pre scroll">{config}</div>
          <div className="row wrap" style={{ marginTop: "var(--s2)" }}>
            <CopyButton text={config} label="Copy MCP JSON" variant="primary" />
            {first?.command && <CopyButton text={first.command} label="Copy agent command" />}
          </div>
        </>
      ) : (
        <p className="muted small">MCP instructions are loading from the local API.</p>
      )}
      {first?.prompt && (
        <details className="prompt-fallback">
          <summary>Setup prompt fallback</summary>
          <div className="pre scroll">{first.prompt}</div>
          <CopyButton text={first.prompt} label="Copy setup prompt" />
        </details>
      )}
    </Card>
  );
}

function SystemHealth({ status, captures }: { status: Status | null; captures: RuntimeEvent[] }) {
  const health = status?.runtime_health;
  const healthLabel = String(health?.status || (health?.ok ? "healthy" : "local"));
  const captureLines = captures.slice(0, 4).map((event) =>
    String(event.summary || event.text || event.event_type || event.type || "captured runtime event"),
  );
  return (
    <Card>
      <p className="eyebrow">Runtime system</p>
      <h2 className="t">Local brain health</h2>
      <div className="health-list">
        <div><span>Server</span><strong>{healthLabel}</strong></div>
        <div><span>BYOK</span><strong>{status?.byok?.has_key ? status.byok.effective_provider : "mock / no key"}</strong></div>
        <div><span>Agent status</span><strong>{status?.agent_status?.status || "not connected"}</strong></div>
        <div><span>Recent captures</span><strong>{captures.length}</strong></div>
      </div>
      {captureLines.length === 0 ? (
        <p className="muted small">No runtime captures are visible yet. Corrections will appear here after agents call capture/feedback tools.</p>
      ) : (
        <ul className="muted small">{captureLines.map((line, index) => <li key={`${line}-${index}`}>{line}</li>)}</ul>
      )}
    </Card>
  );
}

function FeedbackPanel({ activeBrain, name, onChanged }: {
  activeBrain: Status["brains"][number] | null;
  name: string;
  onChanged: () => void;
}) {
  return (
    <Card>
      <p className="eyebrow">Feedback, evals, proposals</p>
      <h2 className="t">Your agent has standards now.</h2>
      <p className="muted small">
        Run the same local judgment loop exposed over MCP: build context, evaluate a draft,
        capture correction, and write proposal-backed learning.
      </p>
      {activeBrain ? <LoopRunner name={name} onChanged={onChanged} /> : (
        <p className="muted small">No brain yet. Connect an agent and build the local brain before running eval feedback.</p>
      )}
      <details className="prompt-fallback">
        <summary>Pending proposals</summary>
        {activeBrain ? <ProposalList name={name} /> : <p className="muted small">No proposals yet.</p>}
      </details>
      <details className="prompt-fallback">
        <summary>Recent improvement log</summary>
        {activeBrain ? <Activity name={name} /> : <p className="muted small">No feedback captured yet.</p>}
      </details>
    </Card>
  );
}

function OssPathCard({ firstClient }: { firstClient: ConnectPrompts["clients"][number] | null }) {
  const prompt = firstClient?.prompt || "";
  return (
    <Card>
      <p className="eyebrow">OSS and hosted path</p>
      <h2 className="t">Free local engine, hosted convenience later.</h2>
      <p className="muted small">
        Catalyst stays useful with no account: local files, localhost server, and MCP tools.
        Hosted Catalyst later adds synced brains and always-on access.
      </p>
      <div className="row wrap">
        <a className="btn btn-primary" href="https://github.com/prathamarchives/catalyst" target="_blank" rel="noreferrer">Try for Free</a>
        <a className="btn btn-glass" href="https://itscatalyst.com" target="_blank" rel="noreferrer">Early Access</a>
        {prompt && <CopyButton text={prompt} label="Copy build prompt" />}
      </div>
    </Card>
  );
}

function LoopRunner({ name, onChanged }: { name: string; onChanged: () => void }) {
  const [task, setTask] = useState("");
  const [packet, setPacket] = useState<BrainContextPacket | null>(null);
  const [draft, setDraft] = useState("");
  const [report, setReport] = useState<HybridEvalResult | null>(null);
  const [fb, setFb] = useState("");
  const [logged, setLogged] = useState<string[] | null>(null);
  const [busy, setBusy] = useState("");

  async function context() {
    setBusy("context");
    setPacket(await api.brainContext(name, task));
    setBusy("");
  }
  async function evaluate() {
    setBusy("eval");
    setReport(await api.evaluate(name, task, draft));
    setBusy("");
  }
  async function feedback() {
    setBusy("fb");
    const r = await api.feedback(name, task, draft, fb);
    setLogged(r.proposal_ids || r.written || [r.error].filter(Boolean));
    setFb("");
    onChanged();
    setBusy("");
  }

  return (
    <div className="loop-runner">
      <Field label="Task" placeholder="e.g. write a launch note for Catalyst" value={task} onChange={(e: any) => setTask(e.target.value)} />
      <Button className="btn-sm" disabled={!task || busy === "context"} onClick={context}>{busy === "context" ? "Building..." : "Build context"}</Button>
      {packet && (
        <div className="pre scroll">
          {JSON.stringify({
            task_type: packet.task_type,
            confidence: packet.confidence,
            sections_loaded: packet.sections_loaded,
            standards: packet.standards.slice(0, 4),
            judgment_rules: packet.judgment_rules.slice(0, 4),
            rejected_patterns: packet.rejected_patterns.slice(0, 4),
            memory_atoms: packet.memory_atoms.slice(0, 6),
            warnings: packet.warnings,
          }, null, 2)}
        </div>
      )}

      <div className="divider" />
      <Field label="Draft output to evaluate" textarea placeholder="Paste a draft to judge against the brain..." value={draft} onChange={(e: any) => setDraft(e.target.value)} />
      <Button className="btn-sm" disabled={!task || !draft || busy === "eval"} onClick={evaluate}>{busy === "eval" ? "Evaluating..." : "Evaluate"}</Button>
      {report && (
        <div className="eval-report">
          <div className="row wrap">
            <Verdict value={report.verdict} />
            {Object.entries(report.scores).map(([k, v]) => <span key={k} className="chip">{k.replace(/_/g, " ")}: {v}/5</span>)}
            <span className="chip">confidence: {Math.round(report.confidence * 100)}%</span>
          </div>
          {report.issues.length > 0 && (
            <ul className="muted small">
              {report.issues.map((issue, n) => <li key={issue.id || n}>{issue.message}</li>)}
            </ul>
          )}
          {report.proposal_ids.length > 0 && <p className="small muted">Proposals: {report.proposal_ids.join(", ")}</p>}
        </div>
      )}

      <div className="divider" />
      <Field label="Correct it" placeholder="e.g. too pitchy, make it more concrete" value={fb} onChange={(e: any) => setFb(e.target.value)} />
      <Button className="btn-sm" disabled={!task || !fb || busy === "fb"} onClick={feedback}>{busy === "fb" ? "Capturing..." : "Capture feedback"}</Button>
      {logged && <p className="small muted">Wrote: {logged.join(", ")}</p>}
    </div>
  );
}

function ProposalList({ name }: { name: string }) {
  const [items, setItems] = useState<Proposal[]>([]);
  const [error, setError] = useState("");

  async function refresh() {
    try {
      setItems((await api.proposals(name)).proposals || []);
      setError("");
    } catch (err: any) {
      setError(err?.message || "Could not load proposals.");
    }
  }

  useEffect(() => {
    refresh();
  }, [name]);

  async function apply(proposal: Proposal, approve: boolean) {
    await api.applyProposal(proposal.id, name, approve);
    await refresh();
  }

  if (error) return <p className="muted small">{error}</p>;
  if (items.length === 0) {
    return <p className="muted small">No pending brain proposals yet. Feedback and evals create proposal-backed changes.</p>;
  }
  return (
    <div className="proposal-list">
      {items.slice(0, 5).map((proposal) => (
        <div className="proposal-row" key={proposal.id}>
          <div>
            <strong>{proposal.target_file}</strong>
            <p className="muted small">{proposal.proposed_change}</p>
            <span className="faint small">{proposal.reason}</span>
          </div>
          <div className="row wrap">
            <Button className="btn-sm" onClick={() => apply(proposal, true)}>Apply</Button>
            <Button className="btn-sm" variant="ghost" onClick={() => apply(proposal, false)}>Reject</Button>
          </div>
        </div>
      ))}
    </div>
  );
}

function Activity({ name }: { name: string }) {
  const [log, setLog] = useState("");
  useEffect(() => {
    api.file(name, "evals/improvement-log.md").then((r) => setLog(r.content || "")).catch(() => {});
  }, [name]);
  const entries = useMemo(() => log.split("## entry").slice(1), [log]);
  return (
    <div>
      {entries.length === 0 && <p className="muted small">No feedback captured yet. Correct an output through your agent or the local loop.</p>}
      {entries.slice(-6).reverse().map((entry, i) => (
        <div key={i} className="pre">{entry.trim().slice(0, 600)}</div>
      ))}
    </div>
  );
}
