const JSON_HEADERS = { "Content-Type": "application/json" };

async function get(path: string): Promise<any> {
  const r = await fetch(path);
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(body.error || `GET ${path} failed`);
  return body;
}
async function post(path: string, body: unknown): Promise<any> {
  const r = await fetch(path, { method: "POST", headers: JSON_HEADERS, body: JSON.stringify(body) });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || `POST ${path} failed`);
  return data;
}

export type RouteResult = {
  task_type: string;
  confidence: number;
  files_to_load: string[];
  why_each_file: Record<string, string>;
  missing_files: string[];
  warnings: string[];
};

export type EvalResult = {
  task_type: string;
  files_loaded: string[];
  verdict: "ship" | "revise" | "reject" | "ask";
  scores: Record<string, number>;
  issues: string[];
  revision_instructions: string[];
  missing_context_questions: string[];
  brain_update_candidates: string[];
};

export type HybridEvalIssue = {
  id?: string;
  severity: string;
  dimension: string;
  message: string;
  evidence?: string;
  suggested_fix?: string;
};
export type HybridEvalResult = {
  verdict: "ship" | "revise" | "reject" | "ask";
  scores: Record<string, number>;
  issues: HybridEvalIssue[];
  matched_rules: string[];
  violated_patterns: string[];
  suggested_feedback: string[];
  proposal_ids: string[];
  confidence: number;
  metadata?: Record<string, unknown>;
};
export type BrainContextPacket = {
  task: string;
  project: string;
  agent: string;
  task_type: string;
  sections_loaded: string[];
  selected_sub_brains: string[];
  standards: Record<string, unknown>[];
  judgment_rules: Record<string, unknown>[];
  rejected_patterns: Record<string, unknown>[];
  approved_examples: Record<string, unknown>[];
  memory_atoms: Record<string, unknown>[];
  instructions_for_agent: string;
  confidence: number;
  warnings: string[];
};
export type BrainSectionSummary = {
  name: string;
  title: string;
  status: string;
  standards: number;
  judgment_rules: number;
  rejected_patterns: number;
  approved_examples: number;
  feedback_memories: number;
  task_patterns: number;
  decision_rules: number;
  context_sources: number;
};
export type BrainSectionsSummary = {
  project: string;
  sections: BrainSectionSummary[];
  health: {
    ok: boolean;
    missing_sections: string[];
    placeholder_sections: string[];
    structured_counts: Record<string, number>;
    warnings: string[];
  };
};
export type Proposal = {
  id: string;
  project?: string;
  target_file: string;
  target_brain?: string;
  proposed_change: string;
  reason: string;
  confidence?: number;
  status: string;
  created_at?: string;
  updated_at?: string;
};
export type CoreHealth = {
  project: string;
  object_count: number;
  edge_count: number;
  evidence_count: number;
  memory_count: number;
  eval_count: number;
  packet_count: number;
  feedback_count: number;
  proof_count: number;
  engine_count: number;
  warning_count: number;
  unprocessed_evidence_count: number;
  orphan_object_count: number;
  low_confidence_count: number;
  stale_count: number;
  by_type: Record<string, number>;
  by_memory_type: Record<string, number>;
  engine_health: { id: string; name: string; status: string; last_run?: string; objects_produced: number; warning_count: number }[];
  warnings: string[];
  next_actions: string[];
};
export type CoreGraph = {
  project: string;
  nodes: { id: string; kind: string; label?: string; status?: string; confidence?: number; memory_type?: string }[];
  edges: { id?: string; from_id: string; to_id: string; type: string; confidence?: number }[];
};

export type Audit = {
  name?: string;
  ready_score: number;
  filled?: number;
  total?: number;
  flags?: Record<string, string[]>;
  distill_recommendation?: string | null;
  summary?: string;
  error?: string;
};

export type BrainFile = { file: string; meta: Record<string, string> };
export type Brain = { name: string; groups: { label: string; files: BrainFile[] }[] };
export type Permissions = {
  mode: "unset" | "recommended" | "manual" | "skip";
  label: string;
  manual_paths: string[];
  updated_at?: string | null;
};
export type ConnectClient = {
  id: string;
  label: string;
  detected: boolean;
  status: string;
  command: string;
  command_label: string;
  prompt: string;
  setup: string;
  note: string;
  mcp_config: Record<string, unknown>;
};
export type ConnectPrompts = {
  repo_root: string;
  server_url: string;
  permissions: Permissions;
  clients: ConnectClient[];
  manual_mcp: Record<string, unknown>;
};
export type BuildStep = {
  id: string;
  label: string;
  state: "pending" | "active" | "done" | "blocked" | "error";
};
export type BuildStatus = {
  name: string;
  status: "waiting" | "building" | "ready" | "blocked" | "error";
  step: string;
  message: string;
  progress: number;
  updated_at?: string | null;
  exists: boolean;
  steps: BuildStep[];
};
export type RuntimeHealth = {
  status?: string;
  ok?: boolean;
  summary?: string;
  project?: string;
  issues?: string[];
  checks?: Record<string, unknown>;
  [key: string]: unknown;
};
export type RuntimeEvent = {
  id?: string;
  type?: string;
  event_type?: string;
  summary?: string;
  text?: string;
  created_at?: string;
  updated_at?: string;
  timestamp?: string;
  [key: string]: unknown;
};
export type RuntimeGraph = {
  summary?: Record<string, unknown>;
  graph?: {
    nodes?: unknown[];
    links?: unknown[];
    edges?: unknown[];
  };
};
export type Status = {
  repo_root: string;
  active_brain?: string;
  brains: { name: string; brain_present: string[]; brain_missing: string[]; has_skills?: boolean; has_workflows?: boolean; has_evals?: boolean }[];
  permissions?: Permissions;
  agent_status?: { agent?: string; status?: string; message?: string; updated_at?: string };
  runtime_health?: RuntimeHealth;
  recent_captures?: RuntimeEvent[];
  brain_file_order?: string[];
  byok: { has_key: boolean; effective_provider: string; mock_mode?: boolean; model?: string };
};

export const api = {
  status: (): Promise<Status> => get("/api/status"),
  agents: () => get("/api/agents/status"),
  health: (): Promise<RuntimeHealth> => get("/api/health"),
  runtimeHealth: (project = "default"): Promise<RuntimeHealth> =>
    get(`/api/runtime/health?project=${encodeURIComponent(project)}`),
  coreHealth: (project = "default"): Promise<CoreHealth> =>
    get(`/api/core/health?project=${encodeURIComponent(project)}`),
  coreGraph: (project = "default"): Promise<CoreGraph> =>
    get(`/api/core/graph?project=${encodeURIComponent(project)}`),
  brainSections: (project = "default"): Promise<BrainSectionsSummary> =>
    get(`/api/brain/sections?project=${encodeURIComponent(project)}`),
  proposals: (project = "default", status = "pending"): Promise<{ proposals: Proposal[] }> =>
    get(`/api/proposals?project=${encodeURIComponent(project)}&status=${encodeURIComponent(status)}`),
  applyProposal: (proposal_id: string, project = "default", approve = true): Promise<any> =>
    post("/api/proposals/apply", { proposal_id, project, approve }),
  events: (): Promise<{ events: RuntimeEvent[] }> => get("/api/events"),
  graph: (): Promise<RuntimeGraph> => get("/api/graph"),
  connectPrompts: (): Promise<ConnectPrompts> => get("/api/connect/prompts"),
  permissions: (): Promise<Permissions> => get("/api/permissions"),
  savePermissions: (payload: { mode: "recommended" | "manual" | "skip"; manual_paths?: string[]; notes?: string }) =>
    post("/api/permissions", payload),
  buildStatus: (name: string): Promise<BuildStatus> => get(`/api/build/status?name=${encodeURIComponent(name)}`),
  extractionPrompt: (): Promise<{ prompt: string }> => get("/api/extraction-prompt"),
  onboarding: (answers: Record<string, string>) => post("/api/onboarding", { answers }),
  brain: (name: string): Promise<Brain> => get(`/api/brain?name=${encodeURIComponent(name)}`),
  file: (name: string, path: string): Promise<{ path: string; content: string; error?: string }> =>
    get(`/api/file?name=${encodeURIComponent(name)}&path=${encodeURIComponent(path)}`),
  saveFile: (name: string, path: string, content: string) => post("/api/file", { name, path, content }),
  importDiscover: (): Promise<{ categories: { category: string; count: number }[]; missing_categories: string[] }> =>
    get("/api/import/discover"),
  importFiles: (name: string, files: { filename: string; text: string }[]) =>
    post("/api/import/files", { name, files }),
  importExtract: (name: string, mode = "manual") => post("/api/import/extract", { name, mode }),
  flowRoute: (name: string, task: string): Promise<RouteResult> =>
    get(`/api/flow/route?name=${encodeURIComponent(name)}&task=${encodeURIComponent(task)}`),
  flowAudit: (name: string): Promise<Audit> => get(`/api/flow/audit?name=${encodeURIComponent(name)}`),
  flowContext: (name: string, task: string, mode = "auto"): Promise<{ packet: string }> =>
    post("/api/flow/context", { name, task, mode }),
  flowEvaluate: (name: string, task: string, output: string, mode = "auto"): Promise<EvalResult> =>
    post("/api/flow/evaluate", { name, task, output, mode }),
  flowFeedback: (name: string, task: string, output: string, feedback: string): Promise<any> =>
    post("/api/flow/feedback", { name, task, output, feedback }),
  brainContext: (project: string, task: string, agent = "control-panel"): Promise<BrainContextPacket> =>
    post("/api/brain/context", { project, task, agent }),
  evaluate: (project: string, task: string, output: string): Promise<HybridEvalResult> =>
    post("/api/evaluate", { project, task, output }),
  feedback: (project: string, task: string, output: string, feedback: string, source = "control-panel"): Promise<any> =>
    post("/api/feedback", { project, task, output, feedback, source }),
};
