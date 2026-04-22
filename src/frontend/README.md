# JoJo Bot v2.0 — Frontend

Next.js 14 App Router. Phase 0 ships only the navigation anchor and four tab placeholders; real UI lands phase by phase.

## Layout

```
app/
├── layout.tsx          ← persistent header + nav (do not edit per-phase)
├── globals.css         ← base styles
├── page.tsx            ← landing page
└── (tabs)/             ← route group so URLs are /wiki, /raw, etc.
    ├── wiki/page.tsx   ← Phase 3 fills in
    ├── raw/page.tsx    ← Phase 3 fills in
    ├── viz/page.tsx    ← Phase 5 fills in
    └── ops/page.tsx    ← Phases 3 + 6 fill in
```

Every placeholder page carries a `phase-tag` badge pointing at the phase that will replace it. The header (`layout.tsx`) is explicitly stable — later phases fill in tab content without touching it.

## Running locally

```bash
cd src/frontend
npm install
npm run dev
# open http://localhost:3000
```

The backend runs separately on port 8000. `next.config.js` rewrites `/api/*` to `http://localhost:8000/api/*` so the same-origin fetch pattern works in dev. Production deployment ships the Next.js build alongside the FastAPI app behind a single entry point.

## Scope boundaries

- **In scope for Phase 0:** nav header, four placeholder pages, styling primitives, backend proxy config.
- **Out of scope for Phase 0:** state management library, auth, data fetching hooks, component library, diff UI, absorb-trigger UI. All arrive with the phase that needs them.

## References

- `ask_jojo/PLAN.md` §6 — phase-by-phase plan for what fills in these placeholders.
- `ask_jojo/docs/ADR/0003-packages-layout.md` — why the Python side uses `packages/` but the frontend uses `src/frontend/`.
