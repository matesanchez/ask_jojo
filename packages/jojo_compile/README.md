# jojo_compile

The absorb loop. Reads raw files from `ask_jojo_raw/` and compiles wiki pages into `ask_jojo_wiki/` according to the constitution in `schema/CLAUDE.md`. Phase 2 owns this package.

## Scope

- `absorb.py` — main entry point, orchestrates fresh-context subagents across the 15-entry checkpoint discipline.
- `plan.py` — subagent that reads a raw entry and proposes which wiki pages to touch.
- `write.py` — subagent that drafts Wikipedia-flat prose with EXTRACTED vs INFERRED claim labels and a 3-quote budget.
- `verify.py` — subagent that cross-checks citations against the raw source before commit.
- `link.py` — post-pass that rebuilds wikilinks, `_index.md`, and `_backlinks.json`.
- `checkpoint.py` — enforces the 15-entry checkpoint; every 15 absorbed raw entries triggers a full pass over touched wiki pages for consistency.
- `breakdown.py` / `reorganize.py` — split overgrown pages, merge undersized ones, migrate schema versions.

## Invariants

- Every wiki claim cites a specific raw file or entry ID.
- No em-dashes, no peacock words. 3-quote budget per page.
- Fresh-context subagents — never reuse a subagent across entries.
- Commit messages use the `absorb:`, `lint:`, `checkpoint:` prefixes authored by `jojo-bot` per ADR 0005.

## Current state

Phase 0 skeleton. CLI stub only.

## References

- `ask_jojo/PLAN.md` §6 Phase 2.
- `ask_jojo/schema/CLAUDE.md` — the constitution every call reads first.
- `ask_jojo/docs/ADR/0001-wiki-over-rag.md` — the design premise.
