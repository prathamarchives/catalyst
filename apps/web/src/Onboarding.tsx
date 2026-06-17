import React, { useEffect, useState } from "react";
import { api } from "./api";
import { Button, Card, CopyButton } from "./components";

// Two screens, no forms: Welcome -> Connect (one copy-paste prompt). The agent
// installs the MCP, scans with approval, builds the brain/skills/evals, and writes
// a how-to-use summary. That's the whole setup.
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
          Not just memory. One prompt connects Catalyst to the agent you already use —
          it scans your workspace, builds your brain, and learns what you'd approve,
          reject, and revise. It gets sharper every time you correct it. Local, private, yours.
        </p>
      </div>
      <div><Button variant="primary" onClick={onStart}>Start</Button></div>
      <p className="faint small">Runs on your machine. No account, no cloud.</p>
    </div>
  );
}

function Connect({ onFinish, onBack }: { onFinish: () => void; onBack: () => void }) {
  const [repo, setRepo] = useState("<repo path>");
  useEffect(() => { api.status().then((s) => setRepo(s.repo_root || "<repo path>")).catch(() => {}); }, []);

  const repoFwd = repo.replace(/\\/g, "/");
  const setupPrompt =
`Set up Catalyst for me, then build my brain.

1. Install the Catalyst MCP server. Run this (use PowerShell on Windows if 'claude' isn't on your shell's PATH):
   claude mcp add catalyst -s user -- py "${repoFwd}/tools/mcp_server.py"

2. Read AGENTS.md and README.md in ${repoFwd}.

3. Discover where my AI sessions, notes, exports, and workspaces live (you can run ${repoFwd}/tools/discover_sessions.py). Show me what you found and recommend a safe scan scope. Do not read any file contents until I approve.

4. With my approval, build my Catalyst brain under ${repoFwd}/outputs/<name>/ — identity, context, goals, constraints, standards, judgment, taste, voice, anti-slop, rejected-examples, decision-rules, task-patterns — plus the skills/ and evals/. Never overwrite anything in templates/.

5. Write ${repoFwd}/outputs/<name>/SUMMARY.md: a short how-to-use (what's in my brain, how you'll use it each task, how I correct it).

From the next session on, use the Catalyst MCP tools (route_task, get_context_packet, review_output_against_brain, append_feedback, audit_brain) on every task: load context before, evaluate after, capture my corrections, keep the brain sharp.`;

  const mcpConfig = JSON.stringify(
    { mcpServers: { catalyst: { command: "py", args: [`${repoFwd}/tools/mcp_server.py`] } } },
    null, 2,
  );

  return (
    <div className="stack" style={{ paddingTop: "var(--s4)" }}>
      <div className="row spread">
        <div className="eyebrow">Connect</div>
        <Button variant="ghost" className="btn-sm" onClick={onBack}>Back</Button>
      </div>
      <div>
        <h1 className="t">One prompt. Your agent does the rest.</h1>
        <p className="lede">
          Paste this into Claude Code (or your agent). It installs Catalyst, scans your
          workspace with your approval, builds your brain, and writes a how-to. No forms.
        </p>
      </div>

      <Card>
        <div className="eyebrow">Copy this to your agent</div>
        <div className="pre scroll" style={{ marginTop: "var(--s2)" }}>{setupPrompt}</div>
        <div className="row wrap" style={{ marginTop: "var(--s2)" }}>
          <CopyButton text={setupPrompt} label="Copy setup prompt" variant="primary" />
          <span className="faint small">Approve the scan when it asks. Your brain appears in the workspace as it builds.</span>
        </div>
      </Card>

      <Card tight>
        <details>
          <summary className="eyebrow" style={{ cursor: "pointer" }}>Not using Claude Code? (manual MCP config)</summary>
          <div style={{ marginTop: "var(--s3)" }}>
            <p className="muted small" style={{ marginTop: 0 }}>Add this MCP server to Cursor or any client, then paste the prompt above and skip step 1.</p>
            <div className="pre">{mcpConfig}</div>
            <div style={{ marginTop: "var(--s2)" }}><CopyButton text={mcpConfig} label="Copy MCP config" /></div>
          </div>
        </details>
      </Card>

      <div className="row"><Button variant="primary" onClick={onFinish}>Open my workspace</Button></div>
    </div>
  );
}
