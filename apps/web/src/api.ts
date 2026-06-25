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
export type Status = {
  repo_root: string;
  active_brain?: string;
  brains: { name: string; brain_present: string[]; brain_missing: string[]; has_skills?: boolean; has_workflows?: boolean; has_evals?: boolean }[];
  permissions?: Permissions;
  byok: { has_key: boolean; effective_provider: string };
};

export const api = {
  status: (): Promise<Status> => get("/api/status"),
  agents: () => get("/api/agents/status"),
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
};
