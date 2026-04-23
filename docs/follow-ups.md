# Follow-ups

**Purpose.** Running list of non-blocking items we've explicitly chosen to defer, with enough context that picking one up later doesn't require re-deriving the decision. Anything blocking is in `docs/v2_status.md` under "Risk Watchlist" instead.

Sorted newest-first. Each entry includes a severity hint (`must` = must ship before the phase that references it; `should` = quality-of-life; `nice` = worth doing if a future pass is nearby), the phase under which it was surfaced, and a clear exit condition.

---

## 2026-04-23 — Phase 1

### FU-5. Verify sibling-repo remote before declaring "pushed"

- **Severity.** should
- **Surfaced while.** running M8 (private-visibility check) of the Phase 1 wrap-up. `gh repo view matesanchez/ask_jojo_raw --json visibility` returned "Could not resolve to a Repository" — not because the visibility was wrong but because the repo had never been pushed at all. `ask_jojo_raw/.git/config` was git-init'd locally with three scaffolding commits on `main` but had no `[remote "origin"]` block. The privacy invariant from ADR 0006 was trivially true (nothing to be public) and also not meaningfully verifiable.
- **Problem.** The Phase 1 deliverables checklist in `v2_status.md` and the wrap-up checklist both assumed `ask_jojo_raw/` was a live GitHub repo from day one. Nothing in our tooling catches the case where a sibling repo is git-init'd but never pushed — the ingest driver writes files, the manifest grows, change records accumulate, and none of it leaves the laptop. One laptop failure = all raw content gone. This would have been silently true right up until we needed the backup.
- **What "done" looks like.** Two layers of defense. (a) Acceptance-style check in `ops/validation/Run-ValidationSyncAll.ps1` or a new `ops/validation/Check-RawRepoRemote.ps1` that runs `git -C "$rawDir" remote -v` and fails loud if empty, plus `gh repo view <org>/<repo> --json visibility,isPrivate` to confirm visibility is PRIVATE. Wire it into the scheduled sync wrapper so Path A scheduled tasks refuse to run if the raw tree is laptop-only. (b) Extend `Install-JojoBot.ps1` with a one-time `gh repo create <org>/<repo> --private --source <rawDir> --remote origin --push` step so greenfield installs land a pushed repo by default.
- **Where to start.** `ops/scheduler/Run-ScheduledSync.ps1` already tees output and writes event-log entries — a 20-line prelude that checks `git -C $rawRepoPath remote -v` slots in cleanly. The installer side is a single new `Ensure-RawRepoRemote` function called from `Install-JojoBot.ps1` step 4-or-5.
- **Why deferred.** Only surfaces as an incident if the laptop dies before we find out — which we just did find out, at Phase 1 exit, while the raw tree is still under 1 GB and easily recreatable. Good enough to file, act on before the 7-day soak accumulates another round of ingest that we'd hate to lose.

### FU-1. Publicdrive walker — streaming writes + timeout

- **Severity.** should
- **Surfaced while.** running the first real `sync-all` against `P:\` on Mateo's laptop — the initial walk ran multi-hour before producing any manifest output.
- **Problem.** `packages/jojo_ingest/drive.py`'s `_walk` yields lazily but `IngestDriver` today batches writes via a single `manifest.save()` call at end-of-run. For a ~100k file tree with per-item conversion, that's hours of "did it crash or is it still walking?" with nothing visible to an operator or to the Raw tab UI.
- **What "done" looks like.** `IngestDriver` flushes change records + manifest updates every N successful entries (N=500 is a reasonable default) so progress is visible mid-run and a mid-walk crash costs only the last N files. Plus a watchdog timeout per-connector (say, 4 hours for publicdrive first-walk; configurable via `config.json`) that fails loud instead of hanging a scheduled task forever.
- **Where to start.** `packages/jojo_ingest/driver.py` — there's one call site for `manifest.save`. A 30-line change plus 1 new test (seed 2000 mock entries, assert manifest.save called ≥4 times).
- **Why deferred.** Not in the Phase 1 exit criterion. First publicdrive walk is a one-time tax; subsequent runs already short-circuit via manifest dedup.

### FU-2. Per-connector singleton lock

- **Severity.** should
- **Surfaced while.** debugging publicdrive status today — observed two `python -m jojo_ingest sync publicdrive` processes alive simultaneously. One was a Microsoft Store Python launcher stub (harmless), but the observation exposes that nothing in the code prevents a real double-invocation from racing the same manifest and change-record files.
- **Problem.** Manifest append-only semantics protect us from straight-up corruption, but two walkers of the same tree will double the I/O, potentially thrash SMB handles on `P:\`, and produce contradictory change records on the same date.
- **What "done" looks like.** A per-connector lock file under `%APPDATA%\JojoBot\locks\<connector>.lock` acquired at the top of each `sync` command. Windows: `msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)` with a friendly "another `sync <connector>` run is in progress (pid N since T)" error; Unix: `fcntl.flock` with `LOCK_EX | LOCK_NB`. Stale-lock detection via pid + start time vs `psutil.Process()` (if the PID is gone, re-claim).
- **Where to start.** New `packages/jojo_core/singleton.py` as a context manager; `jojo_ingest.cli` wraps each `sync` command in it. One new test per platform.
- **Why deferred.** Nice hygiene; not yet seen to cause actual corruption.

### FU-3. Path B — MSAL device-code token provider

- **Severity.** must (for fully unattended SharePoint scheduled runs)
- **Surfaced in.** ADR 0007.
- **Problem.** Delegated tokens from Graph Explorer (Path A) live ~60 minutes. Scheduled SharePoint task re-auths to a dead token between 4h runs until the operator manually pastes a fresh one via `jojo-core config set graph_access_token "<new>"`.
- **What "done" looks like.** `msal_device_code_provider()` slots in behind the existing `TokenProvider` interface. First invocation prompts device-code flow (browser URL + one-time code); thereafter reads `%APPDATA%\JojoBot\tokencache.bin` (DPAPI-sealed per ADR 0009's SECRET_KEYS pattern), silently refreshing the short-lived access token from the long-lived refresh token (~90 days). Scheduler wrapper gains an "auth broken, operator please re-run Install-JojoBot.ps1 -Reconfigure" event-log path.
- **Where to start.** `docs/ops/path-b-msal-device-code-setup.md` already has the dummy's-guide walkthrough of the Entra app registration side. `packages/jojo_ingest/graph.py` is the code-side slot; net new deps: `msal`.
- **Why deferred.** IT hasn't needed to approve the app registration yet (delegated `Sites.Read.All` consent covers Phase 1). Path A gets us through the exit criterion; Path B is the upgrade for fully unattended day-to-day.

### FU-4. ADR 0010 for Path B (if needed)

- **Severity.** nice
- **Surfaced from.** FU-3.
- **Problem.** When Path B ships, ADR 0007 was framed as "start with Path A, track B + C as later paths." The provisioning that unblocks Path B (app registration + consented scopes) plus any operational quirks we discover while deploying are worth capturing — the question is whether that's a new ADR or a follow-up amendment to ADR 0007.
- **What "done" looks like.** Decide at ship time. If Path B ships as drawn in ADR 0007 with no surprises, an amendment note under "Revisit triggers" is enough. If the deploy surfaces new decisions (cert vs secret storage, cache location, refresh-before-expiry window), write ADR 0010.
- **Why deferred.** Premature to write the ADR before the decision exists.

---

## Template for new entries

```
### FU-N. <short title>

- **Severity.** must | should | nice
- **Surfaced while.** <what you were doing when this came up>
- **Problem.** <one paragraph>
- **What "done" looks like.** <concrete acceptance criteria>
- **Where to start.** <file / function / test pointer>
- **Why deferred.** <the reason you're not doing it right now>
```
