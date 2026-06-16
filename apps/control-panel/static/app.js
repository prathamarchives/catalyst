// Catalyst control panel — staged journey. Vanilla JS, local API only.
const App = (() => {
  const STAGES = [
    ["start", "Start"], ["connect", "Connect AI"], ["identity", "Identity"],
    ["context", "Context"], ["permission", "Permission"], ["build", "Build"],
    ["explorer", "Explore"], ["proof", "Proof"], ["mcp", "Agents"],
  ];
  const state = { name: "", answers: { using_for: "writing" }, mode: "mock",
                  modes: [], furthest: 0, brains: [], currentBrain: null, currentFile: null };

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const api = async (p, o) => (await fetch(p, o)).json();
  const esc = (s) => (s || "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  const idx = (name) => STAGES.findIndex((s) => s[0] === name);

  // ---- rail / navigation ----
  function renderSteps() {
    const cur = idx(currentStage());
    $("#steps").innerHTML = STAGES.map(([id, label], i) => {
      const cls = i === cur ? "active" : (i <= state.furthest ? "done" : "");
      const inner = (i < cur || (i <= state.furthest && i !== cur)) ? "✓" : (i + 1);
      return `<button class="step ${cls}" onclick="App.go('${id}')"><span class="num">${i <= state.furthest && i !== cur ? "✓" : i + 1}</span>${label}</button>`;
    }).join("");
  }
  function currentStage() {
    const el = $(".stage.active");
    return el ? el.dataset.stage : "start";
  }
  function go(id) {
    $$(".stage").forEach((s) => s.classList.toggle("active", s.dataset.stage === id));
    state.furthest = Math.max(state.furthest, idx(id));
    renderSteps();
    $("main").scrollTo({ top: 0, behavior: "smooth" });
    const init = { connect: initConnect, permission: () => {}, build: initBuild,
                   explorer: initExplorer, proof: initProof, mcp: initMcp, context: initContext }[id];
    if (init) init();
  }
  function next() { const n = idx(currentStage()) + 1; if (n < STAGES.length) go(STAGES[n][0]); }

  // ---- 0 start ----
  async function initStart() {
    const s = await api("/api/status");
    const repo = (s.repo_root || "").split(/[\\/]/).pop();
    $("#localStatus").textContent = `local · ${repo}`;
    state.brains = s.brains || [];
    $("#installState").innerHTML = `Control panel running locally at <span class="kbd">127.0.0.1</span>. Repo <b>${esc(repo)}</b>. ${state.brains.length ? state.brains.length + " brain(s) on disk." : "No brain yet."} No account, no database.`;
  }

  // ---- 1 connect ----
  async function initConnect() {
    const r = await api("/api/agents/status");
    state.modes = r.modes;
    if (!r.any_live) state.mode = "mock";
    else if (r.byok_has_key) state.mode = "byok";
    renderModes();
    $("#connectMsg").textContent = r.any_live ? "" : "No live model connected — mock/manual mode. Real synthesis needs BYOK or a manual LLM paste.";
  }
  function renderModes() {
    $("#agentModes").innerHTML = state.modes.map((m) => {
      const tag = m.live ? `<span class="tagdot live">live</span>`
        : m.status === "detected" ? `<span class="tagdot">detected</span>`
        : m.status === "needs_key" ? `<span class="tagdot off">needs key</span>`
        : m.status === "not_installed" ? `<span class="tagdot off">not installed</span>`
        : `<span class="tagdot">demo</span>`;
      return `<button class="opt ${state.mode === m.id ? "sel" : ""}" onclick="App.pickMode('${m.id}')">
        <span class="mark"></span>
        <span class="body"><span class="t">${esc(m.label)} ${tag}</span>
        <span class="d">${esc(m.detail)}</span>
        <span class="set">${esc(m.setup)}</span></span></button>`;
    }).join("");
  }
  function pickMode(id) { state.mode = id; renderModes(); }

  // ---- 2 identity ----
  const JOBS = ["coding", "writing", "research", "business", "creative", "operations", "other"];
  function initIdentity() {
    $("#jobChips").innerHTML = JOBS.map((j) =>
      `<span class="chip ${state.answers.using_for === j ? "sel" : ""}" onclick="App.pickJob('${j}')">${j}</span>`).join("");
  }
  function pickJob(j) {
    state.answers.using_for = j;
    $("#idForm [name=using_for]").value = j;
    initIdentity();
  }
  function saveIdentity() {
    const fd = new FormData($("#idForm"));
    const a = Object.fromEntries(fd.entries());
    if (!a.name || !a.name.trim()) { $("#idMsg").textContent = "name is required"; return; }
    state.name = a.name.trim();
    state.answers = { ...state.answers, ...a, using_for: state.answers.using_for };
    next();
  }

  // ---- 3 context ----
  const CONNECTORS = [
    ["Notion", "Export pages as Markdown/CSV, then paste or drop them here.", "export / drop"],
    ["Slack", "Export or paste the channel / customer / team context that matters.", "export / paste"],
    ["Discord", "Export or paste the relevant server / channel context.", "export / paste"],
    ["Local workspace", "Add a folder path above; approve it at the scan step.", "path + approval"],
  ];
  function initContext() {
    $("#connectors").innerHTML = CONNECTORS.map(([t, d, tag]) =>
      `<div class="opt" style="cursor:default"><span class="body"><span class="t">${t} <span class="tagdot off">${tag}</span></span><span class="d">${d}</span></span></div>`).join("");
  }
  async function copyPrompt() {
    const r = await api("/api/extraction-prompt");
    await navigator.clipboard?.writeText(r.prompt || "");
    $("#promptMsg").textContent = "copied ✓";
  }
  async function saveContext() {
    if (!state.name) { $("#ctxMsg").textContent = "set a name in step 2 first"; return; }
    const paths = $("#ctxPaths").value.split("\n").map((s) => s.trim()).filter(Boolean);
    const r = await api("/api/context/save", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: state.name, text: $("#ctxText").value, packet: $("#ctxPacket").value, paths }) });
    $("#ctxMsg").textContent = r.ok ? `saved ${r.written.length} file(s) → outputs/${r.slug}/sources/` : "error: " + (r.error || "?");
    if (r.ok) setTimeout(next, 500);
  }

  // ---- 4 permission ----
  let scanChoice = "recommended";
  function renderScan() {
    const opts = [["recommended", "Approve recommended scan", "AI sessions, notes, markdown workspaces. Safe exclusions on."],
      ["edit", "Edit scope", "Choose categories/paths before any read."],
      ["skip", "Skip scan", "Build from typed + imported context only."]];
    $("#scanChoice").innerHTML = opts.map(([id, t, d]) =>
      `<button class="opt ${scanChoice === id ? "sel" : ""}" onclick="App.pickScan('${id}')"><span class="mark"></span><span class="body"><span class="t">${t}</span><span class="d">${d}</span></span></button>`).join("");
  }
  function pickScan(id) { scanChoice = id; renderScan(); }
  async function discover() {
    $("#discoverOut").innerHTML = `<p class="section-note">discovering (read-only)…</p>`;
    const r = await api("/api/discover");
    const cats = (r.categories || []).map((c) => `<span class="filetag">${esc(c.category)} · ${c.count}</span>`).join(" ");
    $("#discoverOut").innerHTML = `<div class="filetags">${cats || "<span class='section-note'>No known locations in default paths.</span>"}</div><p class="priv" style="margin-top:12px">${esc(r.note || "")}</p>`;
    renderScan();
  }

  // ---- 5 build ----
  function initBuild() {
    const live = state.mode === "byok" && (state.modes.find((m) => m.id === "byok") || {}).live;
    $("#buildMode").innerHTML = live
      ? `Mode: <b>live (BYOK)</b>. Synthesis can use your connected model on approved text.`
      : `Mode: <b>${esc(state.mode)} — mock / no-key seed</b>. The brain is seeded from your typed + imported context. Connect BYOK or use the manual prompt for deeper synthesis.`;
  }
  async function build() {
    if (!state.name) { go("identity"); return; }
    $("#buildStages").innerHTML = `<p class="section-note">building locally…</p>`;
    const r = await api("/api/build", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: state.name, mode: state.mode, answers: state.answers }) });
    state.brains = r.brains || state.brains;
    $("#buildStages").innerHTML = (r.stages || []).map((s) =>
      `<div class="bstage ${s.status === "done" ? "done" : s.status === "skipped" ? "skipped" : ""}">
        <span class="ic">${s.status === "done" ? "✓" : s.status === "skipped" ? "–" : "•"}</span>
        <span><span class="bn">${esc(s.name)}</span><span class="bd">${esc(s.detail)} · ${esc(s.status)}</span></span></div>`).join("");
    $("#buildNext").style.display = "flex";
  }

  // ---- 6 explorer ----
  async function initExplorer() {
    const s = await api("/api/status");
    state.brains = s.brains || [];
    const sel = $("#brainSelect");
    sel.innerHTML = state.brains.map((b) => `<option>${esc(b.name)}</option>`).join("") || `<option value="">no brain yet</option>`;
    if (state.brains.length) loadBrain(state.brains[0].name);
  }
  async function loadBrain(name) {
    if (!name) return;
    state.currentBrain = name;
    const r = await api("/api/brain?name=" + encodeURIComponent(name));
    $("#exnav").innerHTML = (r.groups || []).map((g) =>
      `<div class="exgroup"><h4>${esc(g.label)}</h4>` +
      g.files.map((f) => `<button data-f="${esc(f.file)}" onclick="App.openFile('${esc(f.file)}')">${esc(f.file.replace(".md", ""))}</button>`).join("") +
      `</div>`).join("");
    state._meta = {};
    (r.groups || []).forEach((g) => g.files.forEach((f) => (state._meta[f.file] = f.meta)));
    const first = (r.groups || [])[0]?.files[0]?.file;
    if (first) openFile(first);
  }
  async function openFile(file) {
    state.currentFile = file;
    $$("#exnav button").forEach((b) => b.classList.toggle("active", b.dataset.f === file));
    const r = await api(`/api/file?name=${encodeURIComponent(state.currentBrain)}&path=catalyst-brain/${encodeURIComponent(file)}`);
    const m = (state._meta && state._meta[file]) || {};
    const meta = m["purpose"] ? `${esc(m["purpose"])}` : "";
    const when = m["when to load"] ? ` · loads for: ${esc(m["when to load"])}` : "";
    $("#exmain").innerHTML =
      `<div class="filehead"><div class="fn">${esc(file)}</div><div class="meta">${meta}${when}</div></div>` +
      `<textarea id="fileBody"></textarea>` +
      `<div class="btnrow"><button class="btn small" onclick="App.saveFile()">Save to disk</button><span class="inline-msg" id="saveMsg"></span></div>`;
    $("#fileBody").value = r.content || "";
  }
  async function saveFile() {
    const r = await api("/api/file", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: state.currentBrain, path: "catalyst-brain/" + state.currentFile, content: $("#fileBody").value }) });
    $("#saveMsg").textContent = r.ok ? "saved ✓" : "error: " + (r.error || "?");
  }

  // ---- 7 proof ----
  function initProof() {
    const live = state.mode === "byok" && (state.modes.find((m) => m.id === "byok") || {}).live;
    $("#proofMode").textContent = live ? "live (BYOK)" : "preview (mock — not live AI)";
  }
  async function runProof() {
    const brain = state.brains[0];
    const loaded = brain ? brain.brain_present.filter((f) => /standards|judgment|identity|rejected|taste|constraints|task-patterns/.test(f)) : [];
    const material = `TASK: ${$("#proofTask").value}\n\nDRAFT:\n${$("#proofDraft").value || "(none)"}\n\nReview against: ${loaded.join(", ") || "no brain"}.`;
    $("#proofOut").innerHTML = `<p class="section-note">reviewing…</p>`;
    const r = await api("/api/synthesize", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ section: "standards/judgment review", material }) });
    const live = state.mode === "byok" && (state.modes.find((m) => m.id === "byok") || {}).live;
    $("#proofOut").innerHTML =
      `<div class="panel"><h4>Brain files this task loads</h4><div class="filetags">${loaded.map((f) => `<span class="filetag">${esc(f)}</span>`).join("") || "<span class='section-note'>build a brain first</span>"}</div></div>` +
      `<div class="panel"><h4>Standards review ${live ? "(live BYOK)" : "(mock preview)"}</h4><pre class="code">${esc(r.text || r.error || "")}</pre></div>` +
      `<div class="panel"><h4>What feedback would update</h4><p class="section-note">Your reaction routes to feedback-memory.md, patches standards/judgment/taste, and adds an eval line. That compounding is the difference from a static context file.</p></div>`;
  }

  // ---- 8 mcp ----
  const MCP_TOOLS = [
    ["list_brain_sections", "List the brain's sections grouped by job."],
    ["read_brain_section", "Read one brain file (read-only)."],
    ["review_output_against_brain", "Return the standards checklist + loaded files."],
    ["append_feedback", "Append a feedback rule (only write path)."],
    ["propose_brain_update", "Write a proposal — never overwrites the brain."],
  ];
  async function initMcp() {
    $("#mcpTools").innerHTML = MCP_TOOLS.map(([t, d]) =>
      `<div class="opt" style="cursor:default"><span class="body"><span class="t" style="font-family:var(--mono);font-size:14px">${t}</span><span class="d">${d}</span></span></div>`).join("");
    const r = await api("/api/export");
    $("#exportBlock").textContent = `${r.brain_path}\n\n${r.agent_prompt}`;
  }
  function copy(id) { navigator.clipboard?.writeText($("#" + id).textContent); }

  initStart();
  initIdentity();
  renderSteps();
  return { go, next, pickMode, pickJob, saveIdentity, copyPrompt, saveContext,
           discover, pickScan, build, loadBrain, openFile, saveFile, runProof, copy };
})();
