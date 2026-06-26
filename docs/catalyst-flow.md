# Catalyst flow (v0.5 local app)

The runnable spine of the Catalyst loop. Markdown is still the product; this is the
dependency-free engine so any agent can reproduce it. Local-first, stdlib-only,
writes confined to `outputs/` and `.catalyst/`, templates never written, core
rules never silently mutated.

## What makes this Catalyst (not memory, not a profile)

- **Supermemory** remembers what happened (memory/recall).
- **Creed** remembers who you are (an identity profile).
- **Catalyst** teaches the agent what you would approve, reject, revise — and *how to decide* —
  routing the right standards/judgment/taste for the task, evaluating the output, and
  compounding your corrections into sharper rules. Memory + identity + judgment, together.

## Lifecycle

install → onboard (extract + import) → connect → route → context (+ judgment contract) → evaluate → feedback → proposals → audit/distill

- **install** — clone the repo, run `py catalyst.py` (or `run.cmd` / `run.sh`). The local server starts and the browser opens.
- **onboard** — one flow, two inputs to the same brain: **extract** (answer a few prompts, copy a prompt into any AI, paste the markdown back) and **import** (drop files, paste a dump, or approve discovered local AI sessions). The brain name is the scope, like a container.
- **connect** — copy the MCP config once into your agent (Claude Code / Cursor / …).
- **route** — `catalyst_core.router.route_task` classifies the task (writing/content, reply/dm, strategy/decision, product/build, research/synthesis, design/taste, sales/offer, code/review, life/current-context, unknown/high-stakes) and returns the minimal relevant identity/standards/judgment/taste bundle, with reasons, missing files, warnings. Judgment-aware routing, not vector search.
- **context** — `catalyst_core.packet.build_context_packet` emits a compact packet (identity/context, standards, judgment/rejection rules, taste/voice/anti-slop, constraints) **plus the agent judgment contract** (how to behave/decide/ask/push back) and exact source paths. quick / full / auto.
- **evaluate** — `catalyst_core.evaluator.evaluate_output` scores identity/standards/judgment/taste/anti-slop 0-5 and returns ship | revise | reject | ask. Deterministic, offline; BYOK is an optional adapter.
- **feedback** — `catalyst_core.feedback.capture_feedback` appends a marked entry to `feedback-memory.md` and `evals/improvement-log.md`, and writes a dated proposal under `outputs/<name>/proposals/` classified add | refine | retire. Core rules are never silently overwritten.
- **audit / distill** — `catalyst_core.quality.audit_brain` flags placeholder/thin/stale/duplicate sections, scores readiness, and recommends distillation when feedback piles up. The brain gets sharper, not just longer.

## Persona Brain runtime

The local runtime adds the event-memory loop that agents can call before and
after work:

```txt
recall -> work -> capture -> extract -> update -> compile -> recall
```

- **recall** - `catalyst_core.recall.build_context_packet` selects relevant
  sub-brains and memory atoms for the task.
- **capture** - `catalyst_core.capture.capture_event` appends an event, extracts
  signals, creates or merges memory atoms, routes them into sub-brains, saves
  graph state, compiles markdown, and writes a trace.
- **health** - `catalyst_core.health.get_health` reports events, signals,
  memories, sub-brain maturity, graph counts, orphans, dead links, traces,
  recalls, reviews, and warnings.

Runtime state is local under `.catalyst/`; generated user brains remain under
`outputs/<name>/`.

## Surfaces (one engine)

- **App / UI** — `py catalyst.py` serves the UI and the local API.
- **HTTP API** — `GET /api/flow/route|audit`, `POST /api/flow/context|evaluate|feedback`, `GET /api/health|events|signals|memories|graph`, `POST /api/recall|capture|review`, `GET /api/import/discover`, `POST /api/import/files|extract`.
- **MCP** — tools `route_task`, `get_context_packet`, `review_output_against_brain`, `append_feedback`, `audit_brain`, `propose_brain_update`, plus runtime tools `catalyst_recall`, `catalyst_capture`, `catalyst_search`, `catalyst_profile`, `catalyst_review`, `catalyst_health`, `catalyst_graph`, and `catalyst_propose_update` (`list_brain_sections`, `read_brain_section` too).
- **Dev CLI** — `py tools/catalyst_cli.py <init|status|context|route|evaluate|feedback|audit>`.

All four are thin layers over `catalyst_core`.

## Boundaries

No DB, auth, billing, vectors, embeddings, or required network. Not generic persistent memory;
not "AI writes like you." UI taste is black/white, minimal typography, Apple-like.
