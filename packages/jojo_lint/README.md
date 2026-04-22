# jojo_lint

Wiki linting and self-maintenance. Phase 6 owns this package.

## Scope

Pluggable check registry. Each check implements a common interface (`id`, `severity`, `run(wiki_root) -> Report`) and is scheduled into one of three buckets:

- **Nightly (Sonnet, cheap).** Schema compliance, orphan pages, stub detection, broken wikilinks, bloat (pages > length target), quote budget overruns. Runs automatically via Windows Task Scheduler.
- **Weekly (Opus, expensive).** Cross-page contradiction sweep, staleness detection against raw manifest, missing-article suggestions, "what questions would this wiki fail to answer?" pass.
- **On-commit (fast).** Commit-message-prefix validation (`absorb:` / `lint:` / `checkpoint:` / `[manual]`) cross-referenced against commit author (bot vs human).

## Optional defense-in-depth check

- **Raw repo visibility invariant.** `gh api /repos/<org>/ask_jojo_raw --jq '.visibility'` must return `private`. Fails loud if a future change flips it. Backs ADR 0006.

## Invariants

- Lint reports are idempotent on unchanged input.
- False-positive rate tracked in metrics dashboard; weekly Opus pass targets <10%.
- No check auto-mutates the wiki; every fix goes through the bot-commit path or a human approval.

## Current state

Phase 0 skeleton. CLI stub only.

## References

- `ask_jojo/PLAN.md` §6 Phase 6.
- `ask_jojo/schema/CLAUDE.md` §9 — commit-prefix conventions.
- `ask_jojo/docs/ADR/0006-raw-repo-privacy-invariant.md` — raw-repo visibility invariant.
