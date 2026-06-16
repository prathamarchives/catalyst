# control panel

An optional local control surface for the Catalyst Brain. It is not the product. The product is the markdown protocol in `AGENTS.md`; the panel just makes the brain easy to see and operate. Catalyst works fully without it.

## Why it is built this way

The repo is deliberately dependency-free: markdown plus Python standard library, no npm, no `node_modules`, no build step, no database, no account. A heavy web stack would contradict the positioning (lighter and deeper, optional control surface). So the panel is:

- a single Python stdlib HTTP server (`apps/control-panel/server.py`) — the "bridge"
- a vanilla HTML/CSS/JS single page (`apps/control-panel/static/`)
- zero external dependencies; runs with `py apps/control-panel/server.py`

A richer web app (e.g. `apps/web`) remains a future option once there is demand. The protocol and file layout would not change.

## Run

```txt
py apps/control-panel/server.py
python apps/control-panel/server.py
```

Open `http://127.0.0.1:8765`. It binds `127.0.0.1` only.

## Screens

1. **Status** — brain count, key files present/missing, whether a proof/feedback log exists, BYOK mode, and the visible loop. Quick actions: start onboarding, open brain, run proof, use without UI.
2. **Onboarding** — the 5–7 questions, recommended/manual/skip scan choice, and the default exclusions shown before any read. Builds a seeded brain locally.
3. **Sources** — read-only discovery shown as categories (not path dumps) and the one compact approval question. Supports cautious approval mode and autonomous authorized mode.
4. **Brain explorer** — browse `outputs/<name>/catalyst-brain/*.md`, see each file's purpose / when to load / tasks affected, and edit + save straight to disk.
5. **Proof** — pick a task, see which brain files load, run a standards/judgment review (BYOK or mock), and see what feedback would update.
6. **BYOK** — provider/model/mode, a connection test, and exactly what data is sent if enabled.
7. **Export** — the local brain path and a copy-paste prompt to hand the same brain to any agent without the UI.

## Security

- binds `127.0.0.1` by default; a non-local host refuses to start without `CATALYST_TOKEN`
- no shell or exec endpoint of any kind
- no arbitrary filesystem access: every path is resolved and must stay inside an allowlisted repo-relative root
- reads limited to `outputs/`, `templates/`, `docs/`, `prompts/`
- writes limited to `outputs/` and the local-only `.catalyst/` config; `templates/` are never written (protocol: never overwrite templates)
- the BYOK key is never returned to the browser

## Without the UI

Everything the panel does, an agent can do from `AGENTS.md`. The Export tab exists to make that explicit: the brain is just local markdown.
