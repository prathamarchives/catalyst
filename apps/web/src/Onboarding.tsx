import React, { useEffect, useMemo, useState } from "react";
import { api, BuildStatus, ConnectClient, ConnectPrompts } from "./api";
import { Button, Card, CatalystMark, CopyButton } from "./components";

type Step = "promise" | "connect" | "permissions" | "waiting";

const GITHUB_URL = "https://github.com/prathamarchives/catalyst";
const HOSTED_URL = "https://itscatalyst.com";

export default function Onboarding({ onDone }: { onDone: () => void }) {
  const [step, setStep] = useState<Step>("promise");
  if (step === "promise") return <PromiseScreen onStart={() => setStep("connect")} />;
  return (
    <main className="setup-flow container wide">
      <div className="fade-in" key={step}>
        {step === "connect" && <ConnectScreen onBack={() => setStep("promise")} onNext={() => setStep("permissions")} />}
        {step === "permissions" && <PermissionScreen onBack={() => setStep("connect")} onNext={() => setStep("waiting")} />}
        {step === "waiting" && <WaitingScreen onBack={() => setStep("permissions")} onDone={onDone} />}
      </div>
    </main>
  );
}

function PromiseScreen({ onStart }: { onStart: () => void }) {
  const brainCards = [
    {
      title: "Memory",
      line: "Memory solves context.",
      body: "Work, notes, decisions, references, feedback, and the history your agent usually loses between sessions.",
    },
    {
      title: "Identity",
      line: "Identity tells the agent who it represents.",
      body: "Role, worldview, tone, constraints, direction, voice, and the boundaries it should not cross in your name.",
    },
    {
      title: "Judgement",
      line: "Judgement curates taste.",
      body: "What is good, off-brand, low-signal, cringe, worth revising, or worth shipping.",
    },
  ];
  const story = [
    ["01", "Your agent forgets everything.", "Each new run starts detached from the standards and corrections that shaped the last one."],
    ["02", "Catalyst stores memory.", "Local files and runtime events become a brain agents can recall before they work."],
    ["03", "Catalyst forms identity.", "The agent learns who it represents, what voice to use, and what boundaries matter."],
    ["04", "Catalyst adds judgement.", "Outputs are reviewed against standards, taste, rejected examples, and task-specific rules."],
    ["05", "The brain compounds.", "Feedback becomes proposals, evals, memory, and sharper next-task behavior."],
  ];
  const system = [
    ["Local brain", "Structured wiki sections for identity, context, standards, taste, judgement, feedback memory, and open questions."],
    ["MCP tools", "Agents call recall, capture, review, graph, health, and proposal tools instead of scraping raw files."],
    ["Eval loop", "Drafts are checked against your standards, then corrections are captured as reusable rules."],
    ["Command center", "Health, graph state, build progress, missing sections, and feedback activity stay inspectable locally."],
  ];

  return (
    <main className="landing" id="hero">
      <section className="hero-world">
        <div className="hero-scrim" />
        <div className="hero-inner reveal is-visible">
          <div className="brand-kicker">
            <CatalystMark />
            <span>Local Catalyst Brain for agents</span>
          </div>
          <h1>Identity, memory, and judgement for AI agents.</h1>
          <p className="hero-copy">
            Memory solves context. Identity tells the agent who it represents. Judgement
            curates taste so corrections become local operating rules.
          </p>
          <div className="hero-actions">
            <a className="btn btn-primary btn-lg" href={GITHUB_URL} target="_blank" rel="noreferrer">Try for Free</a>
            <a className="btn btn-glass btn-lg" href="#story">Know More</a>
            <button className="btn btn-ghost btn-lg" type="button" onClick={onStart}>Build Yours</button>
          </div>
          <div className="persona-grid" aria-label="Catalyst brain layers">
            {brainCards.map((card) => (
              <article className="persona-card glass-card" key={card.title}>
                <span className={`artifact-icon ${card.title.toLowerCase()}`} />
                <h2>{card.title}</h2>
                <strong>{card.line}</strong>
                <p>{card.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="world-section story-section" id="story">
        <div className="section-heading reveal">
          <p className="eyebrow">How Catalyst works</p>
          <h2>Your agent gets a brain that can remember, decide, and improve.</h2>
          <p>
            The UI is not a prompt vault. It is a local runtime surface around the loop an agent
            actually uses while working.
          </p>
        </div>
        <div className="story-grid">
          {story.map(([num, title, body]) => (
            <article className="story-card glass-card reveal" key={num}>
              <span>{num}</span>
              <h3>{title}</h3>
              <p>{body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="world-section about-section" id="about">
        <div className="about-copy reveal">
          <p className="eyebrow">About Catalyst</p>
          <h2>Memory alone is not enough.</h2>
          <p>
            Memory helps an agent recover context. Catalyst adds identity and judgement, which
            changes what the agent chooses, rejects, revises, and learns from after the task.
          </p>
          <p>
            The product is local-first: a wiki-style brain, MCP tools, feedback capture, evals,
            and proposals that keep the agent from resetting to generic behavior.
          </p>
        </div>
        <div className="loop-diagram glass-card reveal" aria-label="Catalyst local loop">
          <div className="loop-node home">Agent</div>
          <div className="loop-node">Recall</div>
          <div className="loop-node">Work</div>
          <div className="loop-node">Review</div>
          <div className="loop-node">Capture</div>
          <div className="loop-node">Improve</div>
          <div className="loop-core">
            <CatalystMark />
            <strong>Persona Brain</strong>
            <span>memory + identity + judgement</span>
          </div>
        </div>
      </section>

      <section className="world-section system-section" id="system">
        <div className="section-heading reveal">
          <p className="eyebrow">Command center</p>
          <h2>A tasteful technical object, not an analytics panel.</h2>
          <p>
            Catalyst exposes the local brain, MCP connection, graph health, feedback proposals,
            and eval loop as one inspectable operating layer.
          </p>
        </div>
        <div className="system-grid">
          {system.map(([title, body]) => (
            <article className="system-card glass-card reveal" key={title}>
              <div className="system-line" />
              <h3>{title}</h3>
              <p>{body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="world-section access-section" id="access">
        <div className="access-panel glass-card reveal">
          <div>
            <p className="eyebrow">OSS and early access</p>
            <h2>Run it locally now. Build toward hosted later.</h2>
            <p>
              Local Catalyst is the free engine: one machine, local files, MCP-first setup,
              and no account by default. Hosted Catalyst is the future convenience layer.
            </p>
          </div>
          <div className="access-actions">
            <a className="btn btn-primary" href={GITHUB_URL} target="_blank" rel="noreferrer">Try for Free</a>
            <a className="btn btn-glass" href={HOSTED_URL} target="_blank" rel="noreferrer">Early Access</a>
            <button className="btn" type="button" onClick={onStart}>Build Yours</button>
          </div>
        </div>
      </section>

      <footer className="world-section contact-section" id="contact">
        <div className="contact-card glass-card reveal">
          <CatalystMark />
          <div>
            <p className="eyebrow">Contact</p>
            <h2>Founding installs, collaborations, and agent-brain questions.</h2>
            <p>Reach the team for local installs, creator workflows, product feedback, or hosted access.</p>
          </div>
          <div className="contact-links">
            <a href="mailto:hello@itscatalyst.com">hello@itscatalyst.com</a>
            <a href={GITHUB_URL} target="_blank" rel="noreferrer">GitHub</a>
          </div>
        </div>
      </footer>
    </main>
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
      .catch((err) => setError(err?.message || "Could not load agent connection instructions."));
  }, []);

  const active = useMemo(
    () => data?.clients.find((c) => c.id === activeId) || data?.clients[0],
    [data, activeId],
  );

  return (
    <div className="setup-shell">
      <section className="setup-intro glass-card reveal is-visible">
        <p className="eyebrow">Connect agent</p>
        <h1 className="t">Connect through MCP first.</h1>
        <p className="lede">
          Catalyst is useful when your agent can call the local brain while working. The setup prompt is
          a fallback; the artifact is the MCP connection plus local runtime state.
        </p>
        <div className="setup-route">
          <span>Choose agent</span>
          <span>Add MCP server</span>
          <span>Verify connection</span>
          <span>Build brain</span>
        </div>
      </section>

      <section className="setup-main">
        <div className="row spread wrap">
          <div>
            <p className="eyebrow">Agent access</p>
            <h2 className="t">Pick the client your local agent uses.</h2>
          </div>
          <Button variant="ghost" className="btn-sm" onClick={onBack}>Back</Button>
        </div>

        {error && <Card><p className="muted">{error}</p></Card>}
        {!data && !error && <Card><p className="muted">Loading MCP configuration from the local server...</p></Card>}

        {data && (
          <>
            <div className="tabs" role="tablist" aria-label="Agent choices">
              {data.clients.map((client) => (
                <button
                  key={client.id}
                  className={`tab ${activeId === client.id ? "on" : ""}`}
                  onClick={() => setActiveId(client.id)}
                  type="button"
                  role="tab"
                  aria-selected={activeId === client.id}
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
      </section>
    </div>
  );
}

function AgentCard({ client }: { client: ConnectClient }) {
  const config = JSON.stringify(client.mcp_config, null, 2);
  return (
    <Card className="connect-card">
      <div className="row spread wrap">
        <div>
          <p className="eyebrow">{client.label}</p>
          <h2 className="t">{client.detected ? "MCP path is ready." : "MCP instructions are ready."}</h2>
          <p className="muted small">{client.setup}</p>
        </div>
        <span className={`badge ${client.detected ? "ship" : "ask"}`}>
          <span className="dot" />
          {client.detected ? "detected" : "not detected"}
        </span>
      </div>

      <div className="mcp-grid">
        <div className="mcp-block primary">
          <div className="eyebrow">MCP server config</div>
          <div className="pre scroll">{config}</div>
          <CopyButton text={config} label="Copy MCP JSON" variant="primary" />
        </div>
        <div className="mcp-block">
          <div className="eyebrow">{client.command_label || "MCP command"}</div>
          {client.command ? (
            <>
              <div className="pre">{client.command}</div>
              <CopyButton text={client.command} label="Copy command" />
            </>
          ) : (
            <p className="muted small">No launch command was detected for this client. Use the MCP JSON configuration instead.</p>
          )}
          <p className="faint small">{client.note}</p>
        </div>
      </div>

      <details className="prompt-fallback">
        <summary>Setup prompt fallback</summary>
        <p className="muted small">
          Use this only after the MCP config is in place, or when your client cannot add MCP servers yet.
        </p>
        <div className="pre scroll">{client.prompt}</div>
        <CopyButton text={client.prompt} label="Copy setup prompt" />
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
    <div className="setup-shell">
      <section className="setup-intro glass-card reveal is-visible">
        <p className="eyebrow">Source permission</p>
        <h1 className="t">Choose what the agent may inspect.</h1>
        <p className="lede">
          Discovery can find candidate paths, but content reading stays gated by your scope.
          Catalyst records the permission locally before the agent builds the brain.
        </p>
      </section>

      <section className="setup-main">
        <div className="row spread wrap">
          <p className="eyebrow">Scan scope</p>
          <Button variant="ghost" className="btn-sm" onClick={onBack}>Back</Button>
        </div>

        <div className="choice-grid">
          <Choice title="Recommended safe scan" active={mode === "recommended"} onClick={() => setMode("recommended")}>
            AI sessions, exports, agent memories, markdown workspaces, and notes. Excludes secrets, private DMs, client data, binaries, and vendor folders.
          </Choice>
          <Choice title="Manual paths only" active={mode === "manual"} onClick={() => setMode("manual")}>
            Your agent only reads paths you list. Use this for sensitive machines or tight project scopes.
          </Choice>
          <Choice title="Skip scan" active={mode === "skip"} onClick={() => setMode("skip")}>
            No local content scan. Build from typed context, repo docs, and explicit agent instructions only.
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
      </section>
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
  const [error, setError] = useState("");

  async function refresh() {
    try {
      const s = await api.status();
      const active = s.active_brain || s.brains?.[0]?.name || "me";
      setName(active);
      const b = await api.buildStatus(active);
      setStatus(b);
      setError("");
    } catch (err: any) {
      setError(err?.message || "Could not refresh build status.");
    }
  }

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="setup-shell">
      <section className="setup-intro glass-card reveal is-visible">
        <p className="eyebrow">Build status</p>
        <h1 className="t">Waiting for your agent to build the Catalyst Brain.</h1>
        <p className="lede">
          The command center watches <span className="mono">outputs/{name}/BUILD-STATUS.json</span>.
          Your agent writes the brain; the UI verifies and renders the local state.
        </p>
      </section>
      <section className="setup-main">
        <div className="row spread wrap">
          <Button variant="ghost" className="btn-sm" onClick={onBack}>Back</Button>
          <Button className="btn-sm" onClick={refresh}>Refresh status</Button>
        </div>
        <Card>
          {error && <p className="muted">{error}</p>}
          {status ? <MiniTimeline status={status} /> : <p className="muted">Loading build status...</p>}
          <div className="row wrap" style={{ marginTop: "var(--s3)" }}>
            <Button variant="primary" onClick={onDone}>Open command center</Button>
          </div>
        </Card>
      </section>
    </div>
  );
}

function MiniTimeline({ status }: { status: BuildStatus }) {
  return (
    <div>
      <div className="row spread wrap">
        <div>
          <p className="eyebrow">Current step</p>
          <h2 className="t">{status.status === "waiting" ? "Agent build not started yet" : status.step.replace(/_/g, " ")}</h2>
        </div>
        <span className={`badge ${status.status === "ready" ? "ship" : status.status === "error" ? "reject" : "ask"}`}>
          <span className="dot" />
          {status.status}
        </span>
      </div>
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
