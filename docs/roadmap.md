# roadmap

## v0 — markdown protocol + eval harness (this release)

The agent-runnable protocol: prompts, templates, worked example, before/after proof procedure, and the deterministic eval harness that keeps the repo honest. Repo-as-product; no app, no service, no dependencies.

## v0.1 — stronger examples

More worked examples beyond pratham-mini: different user types (a designer, a newsletter writer, an agency operator), each with a real before/after proof. Examples are the best documentation this protocol can have.

## v0.2 — export guides

Step-by-step guides for getting source material out of the tools people actually use: Claude (claude.ai export + Claude Code sessions), ChatGPT data export, Cursor history, Hermes logs. The biggest current friction is "where do I even get my sessions?" — this version kills it.

## v1 — optional tiny CLI

A small local command-line helper, only if usage proves the need: collect source files into a staging folder, scaffold `outputs/<name>/`, run the eval checks against a generated brain. Strictly optional — the markdown protocol remains the product and must keep working with zero tooling.

## v2 — Catalyst product layer

A product layer on top of the open protocol — only after repeated manual proof with real users and real feedback. The open-source repo stays open and local-first regardless; v2 is for the people who want the loop run for them, not a paywall on the protocol.

## non-goals (any version)

No accounts, no analytics UI, no scraping of private platforms, no "connects to everything" integrations promised before they exist. Scope grows only where proof demands it.
