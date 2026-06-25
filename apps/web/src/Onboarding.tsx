import React, { useEffect, useMemo, useState } from "react";
import { api, BuildStatus, ConnectClient, ConnectPrompts } from "./api";
import { Button, Card, CopyButton } from "./components";

type Step = "promise" | "connect" | "permissions" | "waiting";

export default function Onboarding({ onDone }: { onDone: () => void }) {
  const [step, setStep] = useState<Step>("promise");
  return (
    <div className="container">
      <div className="fade-in" key={step}>
        {step === "promise" && <PromiseScreen onStart={() => setStep("connect")} />}
        {step === "connect" && <ConnectScreen onBack={() => setStep("promise")} onNext={() => setStep("permissions")} />}
        {step === "permissions" && <PermissionScreen onBack={() => setStep("connect")} onNext={() => setStep("waiting")} />}
        {step === "waiting" && <WaitingScreen onBack={() => setStep("permissions")} onDone={onDone} />}
      </div>
    </div>
  );
}

function PromiseScreen({ onStart }: { onStart: () => void }) {
  return (
    <div className="center stack" style={{ paddingTop: "var(--s6)" }}>
      <div>
        <div className="eyebrow">Local Catalyst Brain</div>
        <h1 className="hero">Give your agents your taste, context, and judgment.</h1>
        <p className="lede">
          Catalyst builds a local brain your agents can use to know what you approve,
          reject, revise, and never ship.
        </p>
      </div>
      <div><Button variant="primary" onClick={onStart}>Connect agent</Button></div>
      <p className="faint small">Local files first. Hosted/synced Catalyst comes later.</p>
    </div>
  );
}

function ConnectScreen({ onBack, onNext }: { onBack: () => void; onNext: () => void }) {
  const [data, setData] = useState<ConnectPrompts | null>(null);
  const [error, setError] = useState("");
  const [activeId, setActiveId] = useState("claude-code");

  useEffect(() => {
    api.connectPrompts()
      .then((d) => {
        setData(d);
        setActiveId(d.clients[0]?.id || "manual-mcp");
      })
      .catch((err) => setError(err?.message || "Could not load agent prompts."));
  }, []);

  const active = useMemo(
    () => data?.clients.find((c) => c.id === activeId) || data?.clients[0],
    [data, activeId],
  );

  return (
    <div className="stack" style={{ paddingTop: "var(--s4)" }}>
      <div className="row spread">
        <div className="eyebrow">Connect agent</div>
        <Button variant="ghost" className="btn-sm" onClick={onBack}>Back</Button>
      </div>
      <div>
        <h1 className="t">Your agent builds the brain.</h1>
        <p className="lede">
          Catalyst gives it the protocol, MCP fallback, and build-status contract. The browser
          does not pretend to scan or synthesize on its own.
        </p>
      </div>

      {error && <Card><p className="muted">{error}</p></Card>}
      {!data && !error && <Card><p className="muted">Loading agent instructions...</p></Card>}

      {data && (
        <>
          <div className="tabs" role="tablist" aria-label="Agent choices">
            {data.clients.map((client) => (
              <button
                key={client.id}
                className={`tab ${activeId === client.id ? "on" : ""}`}
                onClick={() => setActiveId(client.id)}
                type="button"
              >
                {client.label}
              </button>
            ))}
          </div>
          {active && <AgentCard client={active} />}
        </>
      )}

      <div className="row spread wrap">
        <Button variant="ghost" onClick={onBack}>Back</Button>
        <Button variant="primary" onClick={onNext}>Choose scan scope</Button>
      </div>
    </div>
  );
}

function AgentCard({ client }: { client: ConnectClient }) {
  const config = JSON.stringify(client.mcp_config, null, 2);
  return (
    <Card>
      <div className="row spread wrap">
        <div>
          <div className="eyebrow">{client.label}</div>
          <h2 className="t" style={{ marginBottom: 0 }}>{client.detected ? "Ready to copy" : "Instructions available"}</h2>
        </div>
        <span className={`badge ${client.detected ? "ship" : "ask"}`}><span className="dot" />{client.detected ? "detected" : "not detected"}</span>
      </div>
      <p className="muted small">{client.setup}</p>

      {client.command && (
        <div style={{ marginTop: "var(--s3)" }}>
          <div className="eyebrow">{client.command_label}</div>
          <div className="pre">{client.command}</div>
          <div style={{ marginTop: "var(--s2)" }}>
            <CopyButton text={client.command} label="Copy command" />
          </div>
        </div>
      )}

      <div style={{ marginTop: "var(--s3)" }}>
        <div className="eyebrow">Copy-paste prompt</div>
        <div className="pre scroll">{client.prompt}</div>
        <div className="row wrap" style={{ marginTop: "var(--s2)" }}>
          <CopyButton text={client.prompt} label="Copy setup prompt" variant="primary" />
          <span className="faint small">{client.note}</span>
        </div>
      </div>

      <details style={{ marginTop: "var(--s3)" }}>
        <summary className="eyebrow" style={{ cursor: "pointer" }}>Manual MCP JSON fallback</summary>
        <div className="pre" style={{ marginTop: "var(--s2)" }}>{config}</div>
        <div style={{ marginTop: "var(--s2)" }}><CopyButton text={config} label="Copy MCP JSON" /></div>
      </details>
    </Card>
  );
}

function PermissionScreen({ onBack, onNext }: { onBack: () => void; onNext: () => void }) {
  const [mode, setMode] = useState<"recommended" | "manual" | "skip">("recommended");
  const [manualPaths, setManualPaths] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function save() {
    setSaving(true);
    setError("");
    try {
      await api.savePermissions({
        mode,
        manual_paths: manualPaths.split(/\r?\n/).map((p) => p.trim()).filter(Boolean),
      });
      onNext();
    } catch (err: any) {
      setError(err?.message || "Could not save permissions.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="stack" style={{ paddingTop: "var(--s4)" }}>
      <div className="row spread">
        <div className="eyebrow">Source permission</div>
        <Button variant="ghost" className="btn-sm" onClick={onBack}>Back</Button>
      </div>
      <div>
        <h1 className="t">Choose what your agent may inspect.</h1>
        <p className="lede">
          Discovery only finds candidate paths. Content reading stays gated by this choice
          and the exclusions stay binding.
        </p>
      </div>

      <div className="choice-grid">
        <Choice title="Recommended safe scan" active={mode === "recommended"} onClick={() => setMode("recommended")}>
          AI sessions, exports, agent memories, markdown workspaces, and notes. Excludes secrets, private DMs, client data, binaries, and vendor/build folders.
        </Choice>
        <Choice title="Manual paths only" active={mode === "manual"} onClick={() => setMode("manual")}>
          Your agent only reads paths you list. Use this for tight project scopes or sensitive machines.
        </Choice>
        <Choice title="Skip scan / use typed context" active={mode === "skip"} onClick={() => setMode("skip")}>
          No local content scan. Build from pasted context and interview answers only.
        </Choice>
      </div>

      {mode === "manual" && (
        <label className="field">
          <span>Manual paths</span>
          <textarea
            className="in mono-area"
            value={manualPaths}
            onChange={(e) => setManualPaths(e.target.value)}
            placeholder="One path per line"
          />
        </label>
      )}

      {error && <p className="muted small">{error}</p>}
      <div className="row spread wrap">
        <Button variant="ghost" onClick={onBack}>Back</Button>
        <Button variant="primary" disabled={saving} onClick={save}>{saving ? "Saving..." : "Save permission"}</Button>
      </div>
    </div>
  );
}

function Choice({ title, active, onClick, children }: {
  title: string;
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button type="button" className={`choice ${active ? "on" : ""}`} onClick={onClick}>
      <span className="choice-title">{title}</span>
      <span className="choice-body">{children}</span>
    </button>
  );
}

function WaitingScreen({ onBack, onDone }: { onBack: () => void; onDone: () => void }) {
  const [name, setName] = useState("me");
  const [status, setStatus] = useState<BuildStatus | null>(null);

  async function refresh() {
    const s = await api.status().catch(() => null);
    const active = s?.active_brain || s?.brains?.[0]?.name || "me";
    setName(active);
    const b = await api.buildStatus(active).catch(() => null);
    setStatus(b);
  }

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="stack" style={{ paddingTop: "var(--s4)" }}>
      <div className="row spread">
        <div className="eyebrow">Build status</div>
        <Button variant="ghost" className="btn-sm" onClick={onBack}>Back</Button>
      </div>
      <Card>
        <h1 className="t">Waiting for your agent to build your Catalyst Brain.</h1>
        <p className="muted">
          Paste the setup prompt into your agent. This page updates automatically as
          <span className="mono"> outputs/{name}/BUILD-STATUS.json</span> appears.
        </p>
        {status && <MiniTimeline status={status} />}
        <div className="row wrap" style={{ marginTop: "var(--s3)" }}>
          <Button variant="primary" onClick={onDone}>Open command center</Button>
          <Button onClick={refresh}>Refresh status</Button>
        </div>
      </Card>
    </div>
  );
}

function MiniTimeline({ status }: { status: BuildStatus }) {
  return (
    <div>
      <div className="progress"><span style={{ width: `${Math.round(status.progress * 100)}%` }} /></div>
      <p className="small muted">{status.message}</p>
      <div className="timeline compact">
        {status.steps.map((step) => (
          <div key={step.id} className={`timeline-step ${step.state}`}>
            <span className="marker" />
            <span>{step.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
