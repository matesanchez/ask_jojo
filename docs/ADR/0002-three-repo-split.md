# ADR 0002 — Three Sibling Repositories (app / wiki / raw)

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** Mateo de los Rios
**Supersedes:** none
**Related:** `ADR 0001` (wiki-over-RAG), `PLAN.md` §3.2, workspace `README.md`

## Context

v2.0 introduces three kinds of content that change at very different rates and for very different reasons:

1. **Application code** — Next.js frontend, FastAPI backend, ingest connectors, compile engine, lint pipeline. Changes on human time (hours to days between commits), via pull-request review.
2. **Compiled wiki** — LLM-authored markdown, maintained automatically by the absorb pipeline. Changes on Claude time (dozens of commits per absorb run, many per day), committed by a service account.
3. **Raw source snapshots** — immutable PDFs, Office docs, markdown from SharePoint / OneDrive / NurixNet. Changes on ingest cadence (every few hours per connector), append-only.

A single repository holding all three would have three properties we do not want: a noisy `git log` that mixes three incompatible rhythms, a coarse access-control model (anyone cloning the app sees every Nurix document we have), and a bundled release process that ties wiki maintenance to code releases.

## Decision

**Split the system into three sibling git repositories**, cloned as siblings inside a parent workspace folder:

```
jojo_bot_v2.0/              ← workspace parent folder (not a git repo)
├── ask_jojo/               ← application code
├── ask_jojo_wiki/          ← compiled knowledge wiki (LLM-authored)
└── ask_jojo_raw/           ← immutable raw source snapshots
```

Each repo has its own remote on GitHub, its own `.gitignore`, its own commit conventions, and its own access control. The app repo depends on the other two at runtime (it reads from `ask_jojo_raw/` and reads/writes to `ask_jojo_wiki/`), but there is no build-time dependency — the three clone independently.

## Rationale

Three different change rates → three different `git log` audiences. A developer reviewing app PRs should not have to filter 200 absorb commits to find the one code change. The absorb pipeline's commits are valuable history for the *wiki* repo, noise for the *app* repo.

Three different access tiers. In the eventual server-mode deployment (Phase 7b), `ask_jojo_raw/` may contain documents that only some employees are permitted to read. Splitting lets us enforce that per-repo with GitHub team permissions, without accidentally giving a frontend contributor read access to every SOP at Nurix.

One compounding artifact. The wiki is the product. If someone wants a backup, an export, or a different frontend, the wiki repo is self-contained. In a monorepo, the wiki would be entangled with the app code and harder to lift out.

Independent release cadences. The app ships via a normal release process; the wiki "releases" with every absorb commit; the raw layer "releases" with every ingest run. Forcing them to align would slow the fastest two to the speed of the slowest.

## Consequences

### Positive

- Clean `git log` per repo. `git blame` is useful.
- Access control is enforced at the repo boundary, which is a well-understood GitHub model.
- The wiki is a portable artifact — clone it alone and it stands on its own.
- Parallelizable review: a code reviewer on `ask_jojo` never waits behind an absorb commit.

### Negative

- Three clones to keep in sync. Developer ergonomics cost, partially offset by the workspace convention (`jojo_bot_v2.0/` parent folder) documented in `README.md`.
- Cross-repo links (wiki citing raw entries) must be by relative path convention, not by GitHub link shortening. The manifest handles this.
- No atomic "commit across all three" — if a change logically spans repos, it lands as three coordinated commits. Acceptable; the cases where this matters are rare.
- A developer cloning just `ask_jojo` cannot run the app end-to-end without the other two repos. Setup docs make this explicit.

## Alternatives Considered

**Monorepo with `app/`, `wiki/`, `raw/` subdirectories.** Rejected. Solves the cloning ergonomics issue but loses every other benefit: `git log` becomes unreadable, access control collapses, wiki portability vanishes, release cadences tangle.

**Submodules.** Rejected. Git submodules with high-frequency automated commits are a known source of pain. The service account pushing to the wiki would force every app-repo consumer to pull and re-pin the submodule pointer constantly.

**Two repos (app + data), wiki and raw bundled together.** Rejected for access-control reasons. Raw sources have a stronger confidentiality profile than the compiled wiki (the wiki filters and paraphrases; raw is verbatim). Splitting them lets us treat them differently if policy requires.

## References

- `PLAN.md` §3.2 "Three Sibling Repositories" and §4 D10 "Git hygiene".
- Workspace `README.md` "Why These Are Separate Repos".
- tig-monorepo (rejected precedent: monorepo model does not fit this system's change rates).
