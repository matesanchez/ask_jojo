# ask_jojo

This repository holds the **application code** for JoJo Bot. It is one of three sibling repositories that together make up the system; the other two (`ask_jojo_wiki/` for the compiled knowledge wiki, `ask_jojo_raw/` for the immutable raw source snapshots) are designed to be cloned alongside this one in the same workspace folder.

## What JoJo Bot Is

JoJo Bot v1.0, already in production, is a Cytiva ÄKTA / protein-purification expert. It answers questions grounded in 232 Cytiva manuals plus a handful of SOPs, using a retrieval-augmented-generation pipeline built on ChromaDB + Claude + GPT-4o, packaged as a Windows `.exe`. That app is not going away; it will continue to answer chromatography questions after v2.0 ships and will sit behind a query router when Phase 4 lands.

JoJo Bot v2.0, being built here, is a broader knowledge hub. Instead of RAG-ing over PDFs at query time, it *compiles* a persistent markdown wiki from SharePoint, OneDrive, the Public Drive, and then answers questions by reading the compiled wiki. The wiki is plain markdown in a git repo, so everything is human-inspectable, version-controlled, and portable. See [`PLAN.md`](./PLAN.md) for the full architecture; see the [frozen ADR](./docs/ADR/0000-v2-roadmap.md) for the ratified plan as of 2026-04-22.

## Where Things Live

| Path | What it is |
| --- | --- |
| `PLAN.md` | The living v2.0 plan. Editable; amendments land as new ADRs. |
| `docs/ADR/0000-v2-roadmap.md` | Frozen copy of the plan at ratification. Do not edit. |
| `docs/ADR/NNNN-*.md` | Subsequent decision records. Numbered sequentially. |
| `docs/v2_status.md` | Living progress tracker against the phases in `PLAN.md`. |
| `schema/CLAUDE.md` | The constitution every Claude API call reads first. Tone, absorb loop, anti-cramming rules, citation discipline. |
| `schema/taxonomy.yaml` | Directory taxonomy for `ask_jojo_wiki/`. |
| `packages/` | (Coming in Phases 1–6) Modular Python packages: `jojo_core`, `jojo_ingest`, `jojo_compile`, `jojo_qa`, `jojo_output`, `jojo_lint`, `jojo_graph`, `jojo_connectors_common`. |
| `src/` | (Existing, from v1.0) Next.js frontend + FastAPI backend that v2.0 extends. |

## Getting Started

You need all three repos cloned as siblings on local disk. The active workspace for this project is:

```
C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\
├── ask_jojo\         ← this repo
├── ask_jojo_wiki\
└── ask_jojo_raw\
```

Do **not** place the workspace inside OneDrive, Dropbox, iCloud, or any other synced folder. Git performs thousands of small file operations per absorb run; sync clients corrupt them.

For v1.0 (the active production app), see the existing v1.0 setup instructions in the legacy `Jojo Bot/` folder at the workspace root. v2.0 dependencies (Python packages for the ingest + compile pipelines, the Next.js IDE tabs, etc.) come online as each phase lands.

## How to Contribute

Read in this order:

1. **[`PLAN.md`](./PLAN.md)** — the living plan. Architecture, phases, exit criteria.
2. **[`docs/v2_status.md`](./docs/v2_status.md)** — what phase we are in, what is blocking.
3. **[`schema/CLAUDE.md`](./schema/CLAUDE.md)** — if you are writing code that will generate a Claude API call, this is mandatory reading.
4. **`ask_jojo_wiki/SCHEMA.md`** (in the sibling repo) — the wiki's operating manual.
5. **[`docs/ADR/`](./docs/ADR/)** — every major design decision, in chronological order.

Design changes that would contradict an earlier ADR require a new ADR. Do not silently override.

## Commit Conventions

Human commits to this repo follow conventional-commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`). Automated commits from the `jojo-bot[bot]` service account use the structured format defined in `ask_jojo_wiki/README.md` (e.g. `absorb(protein-sciences): 8 pages touched, 2 created`). Pre-commit hooks (once wired up in Phase 6) run `jojo_lint schema` against any changes under `schema/` and reject diffs that break the contract.
