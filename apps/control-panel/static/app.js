// Catalyst control panel — vanilla JS, talks to the local allowlisted API.
const App = (() => {
  let state = { brains: [], byok: {}, currentBrain: null, currentFile: null };

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const api = async (path, opts) => {
    const r = await fetch(path, opts);
    return r.json();
  };
  const esc = (s) => (s || "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

  function go(view) {
    $$(".nav button").forEach((b) => b.classList.toggle("active", b.dataset.view === view));
    $$(".view").forEach((v) => v.classList.toggle("active", v.id === "view-" + view));
    if (view === "sources") {} // discovery on demand
    if (view === "export") loadExport();
  }

  async function refresh() {
    const s = await api("/api/status");
    state.brains = s.brains || [];
    state.byok = s.byok || {};
    $("#repo").textContent = (s.repo_root || "").split(/[\\/]/).slice(-1)[0] || "repo";
    renderStatus(s);
    renderBrainSelect();
    renderByok();
  }

  function renderStatus(s) {
    const el = $("#statusCards");
    const b = state.brains;
    const cards = [];
    cards.push(card("Catalyst Brains", `<div class="big">${b.length}</div><div class="muted">under outputs/</div>`));
    if (b.length) {
      const first = b[0];
      const present = first.brain_present.length;
      const total = present + first.brain_missing.length;
      cards.push(card("Key files (" + first.name + ")",
        `<div class="big">${present}/${total}</div>` +
        (first.brain_missing.length ? `<div class="pill miss">missing: ${first.brain_missing.slice(0,3).join(", ")}${first.brain_missing.length>3?"…":""}</div>` : `<div class="pill ok">complete</div>`)));
      cards.push(card("Proof / feedback log", first.last_proof_log
        ? `<span class="pill ok">present</span><div class="muted">evals/improvement-log.md</div>`
        : `<span class="pill warn">none yet</span><div class="muted">run a proof task</div>`));
    } else {
      cards.push(card("No brain yet", `<div class="muted">Start onboarding to build one locally.</div>`));
    }
    cards.push(card("BYOK", `<span class="pill ${state.byok.mock_mode ? "warn" : "ok"}">${state.byok.mock_mode ? "mock (no key)" : esc(state.byok.effective_provider)}</span><div class="muted">${state.byok.mock_mode ? "core works without a key" : esc(state.byok.model || "")}</div>`));
    el.innerHTML = cards.join("");
  }

  const card = (title, body) => `<div class="card"><h3>${title}</h3>${body}</div>`;

  function renderBrainSelect() {
    const sel = $("#brainSelect");
    if (!sel) return;
    sel.innerHTML = state.brains.map((b) => `<option value="${esc(b.name)}">${esc(b.name)}</option>`).join("") || `<option value="">no brain yet</option>`;
    if (state.brains.length && !state.currentBrain) loadBrain(state.brains[0].name);
  }

  // ---- onboarding ----
  $$("#scope label").forEach((l) =>
    l.addEventListener("click", () => {
      $$("#scope label").forEach((x) => x.classList.remove("sel"));
      l.classList.add("sel");
      l.querySelector("input").checked = true;
    })
  );

  async function submitOnboarding(e) {
    e.preventDefault();
    const fd = new FormData($("#onboardForm"));
    const answers = Object.fromEntries(fd.entries());
    $("#onboardMsg").textContent = "building…";
    const res = await api("/api/onboarding", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers }),
    });
    if (res.error) { $("#onboardMsg").textContent = "error: " + res.error; return; }
    $("#onboardMsg").textContent = `built outputs/${res.slug}/ — open the Brain explorer.`;
    await refresh();
    setTimeout(() => go("brain"), 600);
  }

  // ---- sources ----
  async function discover() {
    $("#discoverOut").innerHTML = `<p class="muted">discovering (read-only)…</p>`;
    const r = await api("/api/discover");
    const cats = (r.categories || []).map((c) =>
      `<div class="card spread"><div><b>${esc(c.category)}</b><div class="dim">${c.count} candidate location${c.count>1?"s":""}</div></div><span class="pill ok">found</span></div>`).join("");
    $("#discoverOut").innerHTML =
      `<div class="grid">${cats || `<div class="muted">No known locations found in default paths.</div>`}</div>` +
      `<p class="dim" style="margin-top:10px">${esc(r.note || "")}</p>`;
  }

  // ---- brain explorer ----
  async function loadBrain(name) {
    if (!name) return;
    state.currentBrain = name;
    $("#brainSelect").value = name;
    const r = await api("/api/brain?name=" + encodeURIComponent(name));
    const files = r.files || [];
    $("#brainFiles").innerHTML = files.map((f) =>
      `<button data-file="${esc(f.file)}" onclick="App.openFile('${esc(f.file)}')">${esc(f.file)}</button>`).join("");
    state._meta = Object.fromEntries(files.map((f) => [f.file, f.meta]));
    if (files.length) openFile(files[0].file);
  }

  async function openFile(file) {
    const name = state.currentBrain;
    state.currentFile = file;
    $$("#brainFiles button").forEach((b) => b.classList.toggle("active", b.dataset.file === file));
    const r = await api(`/api/file?name=${encodeURIComponent(name)}&path=catalyst-brain/${encodeURIComponent(file)}`);
    const m = (state._meta && state._meta[file]) || {};
    const metaHtml = ["purpose", "when to load", "tasks affected"].filter((k) => m[k]).map((k) =>
      `<dt>${k}</dt><dd>${esc(m[k]).slice(0,400)}</dd>`).join("");
    $("#brainEditor").innerHTML =
      `<dl class="meta">${metaHtml || "<dd class='muted'>no metadata headers</dd>"}</dl>` +
      `<textarea id="fileBody"></textarea>` +
      `<div class="row" style="margin-top:10px"><button class="btn primary" onclick="App.saveFile()">Save to disk</button><span class="muted" id="saveMsg">catalyst-brain/${esc(file)}</span></div>`;
    $("#fileBody").value = r.content || "";
  }

  async function saveFile() {
    const res = await api("/api/file", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: state.currentBrain, path: "catalyst-brain/" + state.currentFile, content: $("#fileBody").value }),
    });
    $("#saveMsg").textContent = res.ok ? "saved ✓" : "error: " + (res.error || "?");
  }

  // ---- proof ----
  async function runProof() {
    const task = $("#proofTask").value;
    const draft = $("#proofDraft").value;
    const brain = state.brains[0];
    const loaded = brain ? brain.brain_present.filter((f) => /standards|judgment|identity|rejected|taste|constraints|task-patterns/.test(f)) : [];
    const material = `TASK: ${task}\n\nDRAFT:\n${draft || "(none)"}\n\nReview against: ${loaded.join(", ") || "no brain loaded"}.`;
    $("#proofOut").innerHTML = `<p class="muted">reviewing…</p>`;
    const r = await api("/api/synthesize", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ section: "standards/judgment review", material }),
    });
    $("#proofOut").innerHTML =
      `<div class="card"><h3>Brain files this task loads</h3>${loaded.map((f) => `<span class="pill ok" style="margin:2px">${esc(f)}</span>`).join("") || "<span class='muted'>build a brain first</span>"}</div>` +
      `<div class="card" style="margin-top:12px"><h3>Standards review ${state.byok.mock_mode ? "(mock)" : "(BYOK)"}</h3><pre class="out">${esc(r.text || r.error || "")}</pre></div>` +
      `<div class="card" style="margin-top:12px"><h3>What feedback would update</h3><div class="muted">Your reaction routes to: feedback-memory.md, plus a patch to standards/judgment/taste, plus a new eval line. That's the compounding step.</div></div>`;
  }

  // ---- byok ----
  function renderByok() {
    const b = state.byok;
    $("#byokCards").innerHTML = [
      card("Effective provider", `<div class="big">${esc(b.effective_provider || "mock")}</div>`),
      card("Mode", b.mock_mode ? `<span class="pill warn">mock — no network</span>` : `<span class="pill ok">live — BYOK</span>`),
      card("Model", `<div class="muted">${esc(b.model || "—")}</div>`),
    ].join("");
  }
  async function testKey() {
    $("#byokTest").style.display = "block";
    $("#byokTest").textContent = "testing…";
    const r = await api("/api/byok/test", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
    $("#byokTest").textContent = `provider: ${r.provider}\nsent over network: ${r.sent_over_network}\n\n${r.text || r.error || ""}`;
  }

  // ---- export ----
  async function loadExport() {
    const r = await api("/api/export");
    $("#exportPath").textContent = r.brain_path || "outputs/<name>/catalyst-brain/";
    $("#exportPrompt").textContent = r.agent_prompt || "";
  }
  function copy(id) {
    navigator.clipboard?.writeText($("#" + id).textContent);
  }

  // ---- wire up ----
  $$("#nav button").forEach((b) => b.addEventListener("click", () => go(b.dataset.view)));
  $("#onboardForm").addEventListener("submit", submitOnboarding);
  refresh();

  return { go, refresh, discover, loadBrain, openFile, saveFile, runProof, testKey, copy };
})();
