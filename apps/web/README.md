# Catalyst web (consumer UI)

The local, black/white, type-led UI for Catalyst. React + Vite + TypeScript, built to
static `dist/` and served by the local Python server (`apps/control-panel/server.py`).
End users never run npm — `py catalyst.py` serves the prebuilt `dist/` and opens the browser.

## Use (end user)

From the repo root:

```
py catalyst.py
```

The server serves `apps/web/dist/` if present (otherwise the legacy panel at `/legacy`).

## Develop

```
npm install
npm run dev      # Vite dev server on :5173, proxies /api to the Python server on :8765
```

Run the Python server in another terminal (`py apps/control-panel/server.py`) so `/api/*` resolves.

## Ship

```
npm run build    # → apps/web/dist/
```

Commit `dist/` so the app runs without a build step. `node_modules/` is gitignored.

## Structure

- `src/api.ts` — typed fetch wrappers for `/api/*` (flow + import + brain).
- `src/components.tsx` — primitives (Button, Card, Field, Stepper, CopyButton, SectionView, Verdict, ReadinessRing).
- `src/Onboarding.tsx` — the one flow: Welcome → Extract → Import → Review → Connect.
- `src/Workspace.tsx` — brain view, readiness, the live loop runner, activity.
- `src/styles/tokens.css` — design tokens (mono-first, hairlines, type scale).

## Boundaries

No router lib, no state lib, no UI kit — kept lean on purpose. The brain stays local
markdown; this UI only reads/writes it through the allowlisted local API.
