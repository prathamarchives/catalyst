import React, { useEffect, useState } from "react";
import { api, Audit, Brain } from "./api";
import { Button, Card, CopyButton, Field, ReadinessRing, SectionView, Stepper } from "./components";

const STEPS = ["Welcome", "Extract", "Import", "Review", "Connect"];

async function readFiles(list: FileList): Promise<{ filename: string; text: string }[]> {
  return Promise.all(Array.from(list).map(async (f) => ({ filename: f.name, text: await f.text() })));
}

export default function Onboarding({ onDone }: { onDone: (name: string) => void }) {
  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const next = () => setStep((s) => Math.min(STEPS.length - 1, s + 1));
  const back = () => setStep((s) => Math.max(0, s - 1));

  return (
    <div className="container">
      {step > 0 && (
        <div className="row spread" style={{ marginBottom: "var(--s4)" }}>
          <Stepper step={step - 1} total={STEPS.length - 1} label={`${step} of ${STEPS.length - 1} · ${STEPS[step]}`} />
          <Button variant="ghost" className="btn-sm" onClick={back}>Back</Button>
        </div>
      )}
      <div className="fade-in" key={step}>
        {step === 0 && <Welcome onStart={next} />}
        {step === 1 && <Extract name={name} setName={setName} onNext={next} />}
        {step === 2 && <Import name={name} onNext={next} />}
        {step === 3 && <Review name={name} onNext={next} />}
        {step === 4 && <Connect name={name} onFinish={() => onDone(name)} />}
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
        <p className="lede">Not just memory. Catalyst teaches your agent what you'd approve, reject, and revise — and it gets sharper every time you correct it. Local, private, yours.</p>
      </div>
      <div><Button variant="primary" onClick={onStart}>Start</Button></div>
      <p className="faint small">Runs on your machine. No account, no cloud.</p>
    </div>
  );
}

const EXTRACT_FIELDS: { key: string; label: string; hint: string; ph: string }[] = [
  { key: "name", label: "Who is this brain for?", hint: "Your name or handle — becomes the brain's identity.", ph: "e.g. Pratham" },
  { key: "using_for", label: "What will your agent help you do?", hint: "Goals it should pull toward.", ph: "ship a product, write threads, reply to DMs…" },
  { key: "never_ship", label: "What should it never ship?", hint: "Hard limits.", ph: "no hype, no emojis, never pitch in a reply…" },
  { key: "approved_examples", label: "What does great look like?", hint: "Examples or links you'd approve.", ph: "a post/line you love, a link…" },
  { key: "rejected_examples", label: "What do you always reject?", hint: "Highest signal — your standard by contrast.", ph: "rhetorical-question openers, 'in today's world'…" },
  { key: "first_task", label: "A first task you'd hand it", hint: "Seeds a task pattern.", ph: "write a launch post about X" },
];

function Extract({ name, setName, onNext }: { name: string; setName: (s: string) => void; onNext: () => void }) {
  const [a, setA] = useState<Record<string, string>>({});
  const [prompt, setPrompt] = useState("");
  const [pasted, setPasted] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => { api.extractionPrompt().then((r) => setPrompt(r.prompt || "")).catch(() => {}); }, []);
  const nm = (a.name || name).trim();

  async function build() {
    if (!nm) { setErr("Add a name first."); return; }
    setBusy(true); setErr("");
    try {
      const res = await api.onboarding({ ...a, name: nm });
      if (res.error) { setErr(res.error); setBusy(false); return; }
      setName(nm);
      if (pasted.trim()) await api.importFiles(nm, [{ filename: "extracted-brain.md", text: pasted.trim() }]);
      onNext();
    } catch (e) { setErr(String(e)); }
    setBusy(false);
  }

  return (
    <div className="stack">
      <div>
        <h1 className="t">Extract your context</h1>
        <p className="lede">Answer a few sharp questions. This seeds your brain instantly — you can deepen it next.</p>
      </div>
      <Card>
        {EXTRACT_FIELDS.map((f) => (
          <Field key={f.key} label={f.label} hint={f.hint} placeholder={f.ph}
            textarea={f.key !== "name"}
            value={a[f.key] || ""}
            onChange={(e: any) => setA({ ...a, [f.key]: e.target.value })} />
        ))}
      </Card>

      <Card>
        <div className="eyebrow">Optional — deepen with any AI</div>
        <p className="muted small">Copy this prompt into Claude / ChatGPT / Codex, then paste the markdown it returns. It's saved as source material for your agent to distill.</p>
        <div className="row wrap" style={{ margin: "var(--s2) 0" }}>
          <CopyButton text={prompt} label="Copy extraction prompt" />
        </div>
        <Field textarea mono placeholder="Paste the markdown your AI returns (optional)…"
          value={pasted} onChange={(e: any) => setPasted(e.target.value)} />
      </Card>

      {err && <p className="small" style={{ color: "var(--bad)" }}>{err}</p>}
      <div className="row">
        <Button variant="primary" disabled={busy || !nm} onClick={build}>{busy ? "Building…" : "Build my brain"}</Button>
        <span className="faint small">Creates a local brain under outputs/{nm ? nm.toLowerCase().replace(/[^a-z0-9]+/g, "-") : "…"}/</span>
      </div>
    </div>
  );
}

function Import({ name, onNext }: { name: string; onNext: () => void }) {
  const [over, setOver] = useState(false);
  const [written, setWritten] = useState<string[]>([]);
  const [dump, setDump] = useState("");
  const [cats, setCats] = useState<{ category: string; count: number }[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => { api.importDiscover().then((r) => setCats(r.categories || [])).catch(() => {}); }, []);

  async function drop(files: FileList | null) {
    if (!files || !name) return;
    setBusy(true);
    const payload = await readFiles(files);
    const res = await api.importFiles(name, payload);
    setWritten((w) => [...w, ...(res.written || [])]);
    setBusy(false);
  }
  async function saveDump() {
    if (!dump.trim() || !name) return;
    setBusy(true);
    const res = await api.importFiles(name, [{ filename: "pasted-context.md", text: dump.trim() }]);
    setWritten((w) => [...w, ...(res.written || [])]);
    setDump(""); setBusy(false);
  }

  return (
    <div className="stack">
      <div>
        <h1 className="t">Bring what you already have</h1>
        <p className="lede">Drop files, paste a dump, or just skip. All of it becomes source material for your brain.</p>
      </div>

      <div className={`dropzone ${over ? "over" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => { e.preventDefault(); setOver(false); drop(e.dataTransfer.files); }}>
        <p style={{ margin: 0 }}>Drag & drop files here</p>
        <p className="faint small">.md, .txt, .json — notes, exports, existing context. Or
          <label style={{ textDecoration: "underline", cursor: "pointer" }}> browse
            <input type="file" multiple style={{ display: "none" }} onChange={(e) => drop(e.target.files)} />
          </label>
        </p>
      </div>

      <Card>
        <div className="eyebrow">Paste a context dump</div>
        <Field textarea placeholder="Paste anything — a profile, notes, an old context file…" value={dump} onChange={(e: any) => setDump(e.target.value)} />
        <Button className="btn-sm" disabled={busy || !dump.trim()} onClick={saveDump}>Add as source</Button>
      </Card>

      {cats.length > 0 && (
        <Card>
          <div className="eyebrow">Found on your machine (read-only)</div>
          <p className="muted small">Discovered local AI sessions and notes. Nothing was read. Drop or export the ones you want to include above.</p>
          <div className="row wrap">{cats.map((c) => <span key={c.category} className="chip">{c.category} · {c.count}</span>)}</div>
        </Card>
      )}

      {written.length > 0 && <p className="small muted">Imported: {written.join(", ")}</p>}
      <div className="row"><Button variant="primary" onClick={onNext}>Continue</Button>
        <Button variant="ghost" onClick={onNext}>Skip</Button></div>
    </div>
  );
}

function Review({ name, onNext }: { name: string; onNext: () => void }) {
  const [brain, setBrain] = useState<Brain | null>(null);
  const [audit, setAudit] = useState<Audit | null>(null);

  useEffect(() => {
    if (!name) return;
    api.brain(name).then(setBrain).catch(() => {});
    api.flowAudit(name).then(setAudit).catch(() => {});
  }, [name]);

  const placeholders = new Set(Object.entries(audit?.flags || {})
    .filter(([, v]) => v.some((x) => x.includes("placeholder"))).map(([k]) => k));

  return (
    <div className="stack">
      <div className="row spread">
        <div>
          <h1 className="t">Your brain</h1>
          <p className="lede" style={{ marginBottom: 0 }}>{audit?.summary || "Grouped by job. Filled sections are ready; unfilled ones get sharper as you use it."}</p>
        </div>
        {audit && <div className="center"><ReadinessRing score={audit.ready_score} size={56} /><div className="faint small">ready</div></div>}
      </div>

      <Card className="scroll">
        {!brain && <p className="muted">Loading…</p>}
        {brain?.groups.map((g) => (
          <div key={g.label}>
            <div className="group-label">{g.label}</div>
            {g.files.map((f) => (
              <SectionView key={f.file} name={f.file.replace(".md", "")} filled={!placeholders.has(f.file)} />
            ))}
          </div>
        ))}
      </Card>

      <div className="row"><Button variant="primary" onClick={onNext}>Looks good — connect my agent</Button></div>
    </div>
  );
}

function Connect({ name, onFinish }: { name: string; onFinish: () => void }) {
  const [repo, setRepo] = useState("<repo path>");
  useEffect(() => { api.status().then((s) => setRepo(s.repo_root || "<repo path>")).catch(() => {}); }, []);

  const config = JSON.stringify({
    mcpServers: { catalyst: { command: "py", args: ["tools/mcp_server.py"], cwd: repo } },
  }, null, 2);

  return (
    <div className="stack">
      <div>
        <h1 className="t">Connect your agent</h1>
        <p className="lede">Add Catalyst as an MCP server once. Then your agent reads your brain, judges its own output against your standards, and logs your feedback — every task.</p>
      </div>
      <Card>
        <div className="eyebrow">MCP config — Claude Code / Cursor</div>
        <div className="pre">{config}</div>
        <div className="row" style={{ marginTop: "var(--s2)" }}>
          <CopyButton text={config} label="Copy MCP config" variant="primary" />
          <span className="faint small">Paste into your client's MCP settings, pointing at this repo.</span>
        </div>
      </Card>
      <Card>
        <div className="eyebrow">What your agent can now do</div>
        <ul className="muted small" style={{ margin: 0, paddingLeft: "1.1rem" }}>
          <li><span className="mono">route_task</span> — load the right brain files for a task</li>
          <li><span className="mono">get_context_packet</span> — your standards + judgment contract</li>
          <li><span className="mono">review_output_against_brain</span> — verdict + scores</li>
          <li><span className="mono">append_feedback</span> / <span className="mono">audit_brain</span> — capture corrections, keep it sharp</li>
        </ul>
      </Card>
      <div className="row"><Button variant="primary" onClick={onFinish}>Finish — open my workspace</Button></div>
    </div>
  );
}
