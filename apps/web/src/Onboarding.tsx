import React, { useEffect, useState } from "react";
import { api } from "./api";
import { Button, Card, CopyButton } from "./components";

// Two screens, no forms: Welcome -> Connect (MCP). After connecting, the agent does the rest.
export default function Onboarding({ onDone }: { onDone: () => void }) {
  const [step, setStep] = useState(0);
  return (
    <div className="container">
      <div className="fade-in" key={step}>
        {step === 0
          ? <Welcome onStart={() => setStep(1)} />
          : <Connect onFinish={onDone} onBack={() => setStep(0)} />}
      </div>
    </div>
  );
}

function Welcome({ onStart }: { onStart: () => void }) {
  return (
    <div className="center stack" style={{ paddingTop: "var(--s6)" }}>
      <div>
        <div className="eyebrow">Catalyst</div>
        <h1 className="hero">Give your AI your judgment.</h1>
        <p className="lede">
          Not just memory. Connect Catalyst to the agent you already use — it scans your
          workspace, builds your brain, and learns what you'd approve, reject, and revise.
          It gets sharper every time you correct it. Local, private, yours.
        </p>
      </div>
      <div><Button variant="primary" onClick={onStart}>Start</Button></div>
      <p className="faint small">Runs on your machine. No account, no cloud.</p>
    </div>
  );
}

const TOOL_NOTES: { id: string; label: string; note: string }[] = [
  { id: "claude-code", label: "Claude Code", note: "Add to .mcp.json, or run `claude mcp add catalyst -s user -- py <path>` with the command below, then start a fresh session." },
  { id: "cursor", label: "Cursor", note: "Settings → MCP → Add server, paste this config." },
  { id: "other", label: "Other agent", note: "Any MCP client: launch this command as a stdio server." },
];

function Connect({ onFinish, onBack }: { onFinish: () => void; onBack: () => void }) {
  const [repo, setRepo] = useState("<repo path>");
  const [tool, setTool] = useState("claude-code");
  useEffect(() => { api.status().then((s) => setRepo(s.repo_root || "<repo path>")).catch(() => {}); }, []);

  // Absolute path so it connects from any cwd (the server resolves its repo from __file__).
  const script = repo.replace(/\\/g, "/") + "/tools/mcp_server.py";
  const config = JSON.stringify(
    { mcpServers: { catalyst: { command: "py", args: [script] } } },
    null, 2,
  );
  const note = TOOL_NOTES.find((t) => t.id === tool)!.note;

  return (
    <div className="stack" style={{ paddingTop: "var(--s4)" }}>
      <div className="row spread">
        <div className="eyebrow">Connect</div>
        <Button variant="ghost" className="btn-sm" onClick={onBack}>Back</Button>
      </div>
      <div>
        <h1 className="t">Connect Catalyst to your agent.</h1>
        <p className="lede">
          One step. Add Catalyst as an MCP server in the agent you already use. After that it
          does the rest — no forms, no questions.
        </p>
      </div>

      <Card>
        <div className="eyebrow">Add the MCP server</div>
        <div className="row wrap" style={{ margin: "var(--s2) 0" }}>
          {TOOL_NOTES.map((t) => (
            <span key={t.id} className={`chip ${tool === t.id ? "on" : ""}`} onClick={() => setTool(t.id)}>{t.label}</span>
          ))}
        </div>
        <div className="pre">{config}</div>
        <div className="row wrap" style={{ marginTop: "var(--s2)" }}>
          <CopyButton text={config} label="Copy MCP config" variant="primary" />
          <span className="faint small">{note}</span>
        </div>
      </Card>

      <Card>
        <div className="eyebrow">What happens next</div>
        <p className="muted small" style={{ marginTop: 6 }}>Once connected, your agent (guided by Catalyst's instructions + AGENTS.md):</p>
        <ul className="muted small" style={{ margin: 0, paddingLeft: "1.1rem" }}>
          <li>discovers and scans your workspace, AI sessions, and notes — with your approval</li>
          <li>builds your Catalyst brain under <span className="mono">outputs/&lt;name&gt;/</span> and writes its own skills</li>
          <li>runs every task through the loop: load context → produce → evaluate → capture your feedback → improve</li>
        </ul>
        <p className="faint small" style={{ marginTop: "var(--s2)" }}>Your brain appears in the workspace as nodes and fills in as the agent works.</p>
      </Card>

      <div className="row"><Button variant="primary" onClick={onFinish}>Open my workspace</Button></div>
    </div>
  );
}
