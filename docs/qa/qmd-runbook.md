# qmd Activation Runbook

**Status:** Dormant (default). Activates automatically on threshold trip.
**Owners:** Phase 4 retrieval pipeline.
**Governing ADR:** `docs/ADR/0011-qa-via-cowork-while-api-pending.md` and PLAN.md §6 Phase 4 step 5.

This runbook describes how the dormant `qmd` package becomes active in the Q&A retrieval path, what triggers the switch, and how to verify or override it.

## Why qmd is dormant by default

PLAN.md §6 Phase 4 step 5 frames the principle: "we install `qmd` (local BM25 + vector over markdown, Karpathy's recommendation) in Phase 4 but only activate it automatically above the threshold." The wiki is small enough (138 pages today) that index-first retrieval — Sonnet reads the full `_index.md`, picks 3–8 candidates, follows wikilinks 1–2 hops — outperforms BM25/vector on a small corpus. Adding `qmd` before it's needed adds a moving part with no upside.

The qmd activation logic in `packages/jojo_qa/qmd_activation.py` watches three triggers and flips a single config flag (`qmd_active` in `config.json`) when any one of them fires. The runtime retrieval path in `packages/jojo_qa/synthesize.build_retrieval_bundle` reads that flag on every call.

## Triggers

The activation switch flips when *any* of the following holds (per the canonical thresholds in `qmd_activation.py`):

| Trigger | Threshold | Source |
|---|---|---|
| Index size | `_index.md` >= 200 pages | wiki state |
| Latency | p95 of `/api/qa/query` exceeds 8.0 s | benchmark harness writes `qa_p95_latency_sec` to `config.json` |
| Miss rate | > 15% of recent Q&A sessions fall through to raw_fallback (over the last 14 days) | `miss_log.summary()` over `config.qa_session_count` |
| Manual override | `config.qmd_force_active = True` | operator override |

The thresholds are configurable; defaults are above. To experiment with a lower bar, set `qa_p95_latency_sec` or override the threshold via the CLI:

```
jojo-qa qmd status                              # current state
jojo-core config set qmd_force_active true      # manual activate
jojo-core config set qmd_force_active false     # manual deactivate
```

## How activation flows

1. `qmd_activation.check(wiki_root=...)` reads the wiki's `_index.md`, the recent miss log, and any latency stat written to `config.json`.
2. It returns an `ActivationStatus` dataclass with the three triggers' current values, the resulting `active` boolean, and a human-readable `reason`.
3. The Ops tab's `/api/qa/qmd-status` endpoint surfaces this status. The Chat tab shows a "qmd: active|dormant" badge.
4. When a trigger fires *and* the `qmd` package is importable, `should_activate()` returns `True`. The operator then runs `jojo-qa qmd activate` (or the auto-activator job, see below) which writes `qmd_active: true` to `config.json`.
5. The runtime retrieval path checks `is_active()` on each call and prepends a `qmd_prefilter` step before `index_loader.rank_candidates`.

## Auto-activator (post-API-key)

Today the activation step is manual: operator runs `jojo-qa qmd status`, sees a trigger fired, runs `jojo-qa qmd activate`. After the API key lands, a scheduled job in `ops/scheduler/` will run `qmd-status-check.ps1` once a day and auto-activate when any trigger fires.

The auto-activator script is intentionally absent today — manual activation is the right shape until the benchmark harness writes p95 latency reliably and the miss log accumulates enough sessions for the rate to be meaningful.

## Installation (already done)

`qmd` is listed in `pyproject.toml` under the `[qa]` extra. It installs into the venv with:

```
pip install -e ".[qa]"
```

The installation is **idempotent** and **dormant**: no behavior changes until the activation flag flips. Verify installation:

```
python -c "import qmd; print(qmd.__version__)"
```

If the import fails, the activation switch can never flip to `active=True` regardless of trigger state — `qmd_activation.check()` returns `qmd_available=False` and the `reason` field explains. Re-run `pip install -e ".[qa]"` to fix.

## When qmd activates: what changes

Once `qmd_active=true` and `qmd` is importable, the retrieval path changes in exactly one place:

```
# old (dormant): full-index scan
candidates = index_loader.rank_candidates(entries, question, k=8)

# new (active): qmd prefilter -> rank_candidates over the prefilter pool
shortlist = qmd_activation.qmd_prefilter(question, wiki_root, k_shortlist=30)
candidates = index_loader.rank_candidates(
    [e for e in entries if e.slug in shortlist],
    question,
    k=8,
)
```

Everything downstream (retrieval bundle assembly, synthesis prompt, file-back) is unchanged. The shortlist size (30) is wider than the candidate slice (8) so the substring scoring still has discrimination room.

## Building the qmd index

When activation lands, `qmd` needs a one-time corpus build:

```
jojo-qa qmd build      # (TODO when activation lands)
```

This walks `ask_jojo_wiki/`, indexes each page's body and frontmatter, and writes `ask_jojo_wiki/.qmd/`. The directory is in `.jojoignore` and `.gitignore` so it doesn't pollute the wiki repo. Subsequent absorb runs trigger an incremental qmd reindex via a checkpoint hook.

## Rollback

To deactivate qmd in production:

```
jojo-qa qmd deactivate
```

The retrieval path falls back to the index-first path on the next call. No restart needed. The qmd index files remain on disk so re-activating is instant.

If a deeper rollback is needed (e.g. qmd is producing bad shortlists and we want to remove the package entirely), uninstall via:

```
pip uninstall qmd
```

`qmd_activation.check()` will then report `qmd_available=False`, and the runtime path falls back to index-first regardless of the activation flag.

## Triggers we explicitly didn't add

Two triggers were considered and rejected:

- **Page count by directory.** A directory bloating past 50 pages was originally going to be a trigger. Rejected because directory growth is a *re-organization* signal (handled by the absorb pipeline's reorganize pass per `schema/CLAUDE.md` §3) rather than a *retrieval* signal. The miss log catches retrieval problems; directory bloat is its own thing.
- **Token budget per question.** A retrieval bundle exceeding N tokens would prefilter via qmd to shrink it. Rejected because the budget model (`docs/budget-model.xlsx`) suggests we're nowhere near token-budget limits with 138 pages, and the cleaner cause-vs-effect signal is index size, which directly correlates with bundle size.

If a future operator finds a real-world signal we missed, add it to `qmd_activation.check()` and document it here.
