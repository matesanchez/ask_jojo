# Compile Prompt — Paste-In Template for Cowork Absorb Sessions

**Status:** v0.1, 2026-04-24
**Purpose:** Self-contained prompt Mateo pastes into a fresh Cowork session to run one Phase 2 absorb batch against the Protein Sciences corpus. Each session processes one batch of entries from `docs/compile/queue.md`, writes pages into `ask_jojo_wiki/`, and commits.
**Governing ADR:** `docs/ADR/0010-compile-via-cowork-while-api-pending.md`
**Change discipline:** Every time a session surfaces a gap in these instructions (ambiguous taxonomy call, unclear citation rule, new edge case), update this file and commit it *before* the next session runs. The prompt is a living specification.

---

## How to use this file

1. Open a fresh Cowork window with the `jojo_bot_v2.0` folder selected.
2. Copy everything between the two `=== PASTE BELOW ===` / `=== PASTE ABOVE ===` markers.
3. Paste it as the first message into the new session.
4. When the session reports "batch complete," review the diff in `ask_jojo_wiki/`, run `git log -1` to check the commit message, and either push or amend.
5. If something went wrong, revert the commit (`git reset --hard HEAD~1`) and update this file with whatever guidance would have prevented it.

Sessions are single-purpose: one batch, then stop. Do not reuse a session across batches — the context window bloats and the per-page attention gets worse.

---

## === PASTE BELOW ===

You are running a Phase 2 wiki-absorb session for the JoJo Bot v2.0 project. This session has one job: take the next unchecked batch from `ask_jojo/docs/compile/queue.md`, read the listed raw entries from `ask_jojo/ask_jojo_raw/`, and write new or updated pages into `ask_jojo_wiki/` following the schema and style rules below. Then commit. Then stop.

**Before you write anything,** read these four files in full (in this order):

1. `ask_jojo/schema/CLAUDE.md` — the wiki constitution. The absorb loop, the 15-entry checkpoint, EXTRACTED vs INFERRED discipline, the writing style rules, contradiction handling, and the commit convention all live there. Treat it as authoritative; if anything in this prompt appears to contradict it, the constitution wins and you should flag the conflict at the end of the session.
2. `ask_jojo_wiki/SCHEMA.md` — the wiki operating manual. Directory layout, frontmatter schema (every field), page-type table, citation format, wikilink conventions, length targets.
3. `ask_jojo/schema/taxonomy.yaml` — the starter directory taxonomy. Directory names are plural, kebab-case. If a page doesn't fit any existing directory, follow the constitution's rule: propose the new directory in your absorb plan and add it to `taxonomy.yaml` as part of the commit.
4. `ask_jojo/docs/compile/queue.md` — the batch tracker. Find the first unchecked batch (the top `## Batch N` heading whose entries are not all ticked). That batch is yours. If every batch is ticked, stop immediately and report "queue empty."

Then read, if they exist:

- `ask_jojo_wiki/_index.md` — catalog of pages that already exist. If the file is missing, seed it as an empty table at the end of the session (one row per page you wrote).
- `ask_jojo_wiki/_backlinks.json` — reverse-link index. Same rule: seed it at session end as `{}` if missing.

### Absorb loop (per entry in your batch)

For each entry in the claimed batch, in order:

1. **Read the raw entry.** Full file, including frontmatter. The source identifier, URL, and fetched-date all come from the raw frontmatter — these become your citation. Note the `access_level` (`all_fte` for everything in Phase 2 per `ADR 0006`).
2. **Read any existing wiki pages the entry might touch.** Search `ask_jojo_wiki/` for pages whose slug matches obvious subjects from the raw entry (program names, target names, method names, equipment names). Open the whole page, including frontmatter and existing sources list. You are integrating into existing structure, not appending.
3. **Plan.** Before writing, decide: does this entry update existing pages (most common), create new pages, or both? Which claims are EXTRACTED (stated verbatim or near-verbatim in the source) vs INFERRED (your synthesis across multiple statements)? What's the taxonomy target directory for any new page? Write the plan as a short comment in your working notes; don't commit it, but keep it visible to yourself.
4. **Write.** Use the frontmatter schema in `SCHEMA.md` §3. Every file is UTF-8, no BOM. Kebab-case slugs. `created` is today's date (`2026-04-24` or whatever today is; run `date +%Y-%m-%d` in the shell if unsure). `last_updated` and `last_reviewed` are also today. `schema_version: 0.1.0`. `corpus: protein-sciences`. `confidence: high | medium | low` per your honest judgment — medium is the default when a claim rests on a single source; low is for claims that smell like inference beyond what the source supports. Cite every paragraph at least once, in the format `SCHEMA.md` §7 specifies.
5. **Verify.** Re-read what you just wrote. For every factual claim, ask: is it in a cited source? If not, either find a source for it or delete it. This is the line between a wiki and a hallucination generator.
6. **Link.** Add wikilinks `[[Target Page Title]]` for any entity the new/updated content mentions that has (or will have) its own page. Don't invent links to pages you don't plan to create. Add an entry to `_index.md` for any page you created.
7. **Tick the box** in `queue.md` for that entry. Use `- [x]` — GitHub-flavored markdown.

Do this for every entry in the batch. Stop at the batch boundary.

### Writing style (enforced by `schema/CLAUDE.md`, surfaced here)

- No em-dashes (`—`). Use commas, periods, or parentheses.
- No peacock words: "leverage", "robust", "cutting-edge", "unparalleled", "groundbreaking", "best-in-class". Prefer plain language.
- No "synergize", "utilize" when "use" works, "in order to" when "to" works.
- No bullet points for prose. Use paragraphs. Bullets are fine for genuinely enumerable lists (reagents, steps in a protocol, equipment model numbers).
- Third person. Past tense for events, present tense for facts. No first-person ("we did", "our lab") — the wiki is organizational memory, not a lab notebook.
- Dates in ISO format (`2025-03-10`), never "March 10, 2025" or "3/10/25".
- Don't chronicle source additions. If source A and source B both say TYK2 is a kinase, the page says "TYK2 is a kinase" and cites both. It does *not* say "Source A established that TYK2 is a kinase. Source B confirmed in 2023."

### Citation discipline

- Every paragraph has at least one citation. No uncited claims. Ever.
- Citation format is the one in `SCHEMA.md` §7. Cross-check before committing.
- EXTRACTED vs INFERRED: mark inference explicitly in the paragraph ("The protein yields imply…" is INFERRED; "The 2025 goals document lists 48-clone expression as a target" is EXTRACTED). If you can't tell, it's INFERRED — default conservative.
- Conflicting sources: follow `schema/CLAUDE.md` contradiction policy. Both are cited, the conflict is noted, confidence drops to `medium` or `low`, the page flags itself for review. Never silently pick one.

### Commit convention

When the batch is complete, commit with the constitutional format from `schema/CLAUDE.md` §9:

```
absorb(protein-sciences): <N> pages touched, <M> created

Batch <N> of docs/compile/queue.md.
Entries absorbed: <entry_id_1>, <entry_id_2>, ...

Co-Authored-By: Claude Sonnet 4.6 via Cowork <noreply@anthropic.com>
```

One commit per batch. Do not commit schema changes, queue changes, and wiki changes in separate commits — keep the batch atomic so `git revert <sha>` undoes the whole batch cleanly.

Two repos will have changes: `ask_jojo/` (queue.md tick marks, possibly taxonomy.yaml, possibly this prompt file) and `ask_jojo_wiki/` (the pages). Commit in each repo separately, same format in each. Do **not** push — Mateo pushes after reviewing.

### Stop conditions

Stop and report, in this order of priority:

1. **Constitutional conflict.** This prompt and `schema/CLAUDE.md` disagree. Surface the conflict verbatim; do not write pages.
2. **Queue empty.** Every batch is ticked. Report and stop.
3. **Source unreadable.** A raw entry is missing, malformed, or too redacted to extract useful content. Skip that entry, tick its box with a note `- [x] <id> — skipped: <reason>`, continue with the rest of the batch.
4. **Taxonomy gap.** The batch requires a directory that doesn't exist in `taxonomy.yaml` and you're not confident proposing a new one. Surface the gap; do not force-fit into an adjacent directory.
5. **Batch complete.** Normal termination. Commit, report page counts, stop.

Do not run further batches after completing yours. Do not `git push`. Do not modify anything outside `ask_jojo_wiki/` (wiki pages, `_index.md`, `_backlinks.json`) and `ask_jojo/docs/compile/queue.md`, except the two living-spec exceptions: `ask_jojo/schema/taxonomy.yaml` (if you added a directory) and `ask_jojo/docs/compile/compile-prompt.md` (if you want to propose a tightening — surface the proposal in the session log, don't silently edit).

### What success looks like

At the end of the session, the operator (Mateo) should be able to:

1. Run `git status` in `ask_jojo/` and `ask_jojo_wiki/` and see only the expected changes.
2. Run `git diff HEAD~1` and see pages that read like a single smart author wrote them after reading the sources.
3. Spot-check three random paragraphs and find citations that trace back to real raw files.
4. See the queue file with the processed batch's boxes ticked.
5. Push both repos with no further edits.

If any of those fail, the session did not succeed regardless of what it thinks it did.

## === PASTE ABOVE ===

---

## Change log for this prompt

Every change to the paste-in block above is a change to Phase 2's output contract. Log it here.

| Date | Change | Reason |
| --- | --- | --- |
| 2026-04-24 | v0.1 initial draft | Seed for Phase 2 kickoff (ADR 0010). |
