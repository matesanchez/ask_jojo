# Phase 2 — Public Drive Through Phase 2 Exit (paste-in prompts)

**Status:** v0.1, 2026-04-27
**Purpose:** Five sequential paste-ready prompts that walk Phase 2 from the freshly-scraped Public Drive corpus through Phase 2 exit. Each prompt opens a fresh Cowork session with the `jojo_bot_v2.0` folder selected and is self-contained: no prior conversation context required. Run them in order. Push between prompts.
**Governing specs (do not redefine in any prompt; the prompts cite them):**
- `ask_jojo/PLAN.md` §6 Phase 2 — phase deliverables, four-step pipeline, anti-patterns, cross-walk, exit criterion.
- `ask_jojo/schema/CLAUDE.md` — absorb loop, 15-entry checkpoint, writing style, citation discipline, commit-message format.
- `ask_jojo_wiki/SCHEMA.md` — frontmatter schema, page-type table, citation format, length targets.
- `ask_jojo/schema/taxonomy.yaml` — directory taxonomy.
- `ask_jojo/docs/compile/queue.md` — batch tracker.
- `ask_jojo/docs/compile/compile-prompt.md` — canonical single-batch absorb prompt (Prompt 2 below extends it for the long-tail loop).
- `ask_jojo/docs/ADR/0010-compile-via-cowork-while-api-pending.md` — why this loop runs in Cowork.

**Constitutional invariants every prompt must enforce.**

1. Commit-message subjects: `absorb(protein-sciences):` for absorb work; `checkpoint:` for checkpoint commits; `lint:` / `lint(opus):` for lint passes; `[manual]` for human overrides. Wiki absorb-batch commits use the exact subject form from `schema/CLAUDE.md` §9: `absorb(protein-sciences): N pages touched, M created`.
2. Co-author trailer, exact line: `Co-Authored-By: Claude Sonnet 4.6 via Cowork <noreply@anthropic.com>`.
3. Author override for Cowork-authored commits: `git -c user.email='cowork@anthropic.com' -c user.name='Cowork' commit ...`.
4. No `--amend`, no `--force`, no `rebase`, no `git config` writes. Fix-forward with new commits.
5. Wiki style enforced: no em-dashes (`—`), no peacock words, declarative third-person, ISO dates, citations marked EXTRACTED vs INFERRED with source IDs and SHA256 hash prefixes (first 16 chars of `sha256sum ask_jojo_raw/<connector>/<id>.md`).
6. Wikilinks use bare slug form: `[[bare-slug|Display Title]]` — no folder prefix.
7. Truthful queue: every manifest entry is ticked one way or another (`- [x]` for absorbed, `- [x] <id>  <!-- skip: <reason> -->` for skip-pooled).
8. Sandbox-quirk: before every `git commit` use the lock-cleanup snippet (FUSE filesystem disallows `unlink`):
   ```python
   import os, glob
   for ln in ['.git/index.lock', '.git/HEAD.lock', '.git/objects/maintenance.lock']:
       try:
           tmp = ln + '.tmp'
           with open(tmp, 'wb') as f: f.write(b'')
           os.replace(tmp, ln); os.rename(ln, ln + '.kill')
       except FileNotFoundError: pass
   for p in glob.glob('.git/next-index-*.lock'):
       try: os.rename(p, p + '.kill')
       except: pass
   ```
   And use `dangerouslyDisableSandbox: true` on Bash calls that involve `git commit`.

---

## Prompt 1 — Reconcile state and author the Public Drive batches

Run this once after the scheduler has finished its first clean Public Drive walk. It rebuilds `manifest.json` from the on-disk raws (the 2026-04-25 walk crashed mid-save and left the manifest with only a partial publicdrive snapshot, missing the prior onedrive + sharepoint coverage), validates the corpus, then authors a sequence of `## Batch N — Public Drive ...` blocks in `ask_jojo/docs/compile/queue.md` covering every publicdrive manifest entry.

### === PASTE BELOW ===

You are in a fresh Cowork session for the JoJo Bot v2.0 project, with the `jojo_bot_v2.0` folder selected. This session has one job: reconcile the corpus state after the 2026-04-25 publicdrive sync, then divide the Public Drive content into topical absorb-batches. Do NOT absorb anything in this session. The output is queue.md edits + a manifest rebuild + commits.

**Working tree.** Three sibling repos under the selected folder: `ask_jojo/`, `ask_jojo_raw/`, `ask_jojo_wiki/`. The Public Drive raws live in `ask_jojo_raw/publicdrive/*.md`. The OneDrive raws live in `ask_jojo_raw/onedrive/*.md`. The SharePoint raws live in `ask_jojo_raw/sharepoint/*.md`. The manifest at `ask_jojo_raw/manifest.json` is the ground-truth index but needs rebuilding (see step 1).

**Read first** (in this order, full files):

1. `ask_jojo/PLAN.md` §6 Phase 2 — phase deliverables, four-step pipeline, anti-patterns, cross-walk, exit criterion.
2. `ask_jojo/schema/CLAUDE.md` — absorb loop, 15-entry checkpoint, writing style, citation discipline, commit format.
3. `ask_jojo/docs/compile/queue.md` — read the existing Batch 1 through Batch 23 to internalize the cluster-of-related-entries structure. Batch 23 (the OneDrive long-tail) is the closest precedent for what you are about to write: large corpus, themed clusters, absorb-pool vs skip-pool split, theme paragraphs that explain the split.
4. `ask_jojo/docs/compile/compile-prompt.md` — the canonical single-batch absorb prompt; the queue's per-batch metadata block has to align with it.

### Stage 1 — Rebuild and validate `ask_jojo_raw/manifest.json`

The 2026-04-25 publicdrive sync wrote 7,221 new files and ~4 updates per the `_changes/2026-04-25.json` journal, but its manifest save crashed mid-write — the resulting `manifest.json` contains a partial JSON object followed by trailing data, parses to only 14,681 publicdrive + 313 sharepoint entries, and is missing the 18,112 onedrive + remaining 1,310 sharepoint files that still sit on disk under `ask_jojo_raw/onedrive/` and `ask_jojo_raw/sharepoint/`.

Rebuild the manifest by walking the on-disk raws. Each `.md` file under `ask_jojo_raw/<connector>/` has a frontmatter block; the manifest entry is derived from that frontmatter plus the file's SHA256. Schema for a manifest entry is the existing entries' shape (path, sha256, source_type, source_url, source_id, title, access_level, fetched, size_bytes, redacted_fields, supersedes). A rebuilder script lives roughly here:

```python
import hashlib, json, re
from pathlib import Path
import yaml  # pip install pyyaml if missing

raw = Path("ask_jojo_raw")
entries = {}
for connector in ("onedrive", "sharepoint", "publicdrive"):
    cdir = raw / connector
    if not cdir.exists():
        print(f"  (no {connector}/ on disk; skipping)")
        continue
    n = 0
    for path in sorted(cdir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            print(f"  WARN: no frontmatter in {path.name}")
            continue
        end = text.index("\n---\n", 4)
        fm = yaml.safe_load(text[4:end]) or {}
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        # canonical_sha256 normalizes trailing whitespace / line endings; the
        # raw .md as-on-disk is what the original walk hashed, so the file's
        # sha matches its frontmatter.sha256 at write time. Cross-check.
        eid = path.stem  # entry_id is the file stem
        entries[eid] = {
            "path": f"{connector}/{path.name}",
            "sha256": fm.get("sha256") or sha,
            "source_type": fm.get("source_type") or connector,
            "source_url": fm.get("source_url", ""),
            "source_id": fm.get("source_id", ""),
            "title": fm.get("title", ""),
            "access_level": fm.get("access_level", "all_fte"),
            "fetched": fm.get("fetched", ""),
            "size_bytes": path.stat().st_size,
            "redacted_fields": fm.get("redacted_fields", []) or [],
            "supersedes": fm.get("supersedes"),
        }
        n += 1
    print(f"  {connector}: {n} entries")

manifest = {
    "schema_version": "0.1.0",
    "generated": "<UTC ISO timestamp>",
    "entries": entries,
    "supersedence": {},
}
(raw / "manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(f"wrote {len(entries)} total entries")
```

After rebuilding, sanity-check:

- Total entries should be roughly `18112 + 1623 + ~15000 ≈ 34,500`. If publicdrive count is wildly off from the on-disk file count, halt and surface.
- Spot-check 5 random entries: open the .md file, confirm frontmatter parses, confirm the manifest entry's sha256 matches a fresh `sha256sum` of the file.
- If any frontmatter fails to parse, log the path and skip it — but report the count so the operator can investigate.

Commit the rebuilt manifest in `ask_jojo_raw/`:
```
chore(manifest): rebuild manifest.json from on-disk raws (post-2026-04-25 sync)

Reason: the 2026-04-25 publicdrive sync crashed mid-save and left
manifest.json with only a partial publicdrive snapshot; the on-disk
raws under onedrive/, sharepoint/, and publicdrive/ are intact.
Walked the three connector directories, parsed frontmatter, recomputed
sha256 per file, and wrote a fresh manifest.

  onedrive: <N>
  sharepoint: <M>
  publicdrive: <K>
  total: <N+M+K>

Co-Authored-By: Claude Sonnet 4.6 via Cowork <noreply@anthropic.com>
```

### Stage 2 — Triage the Public Drive corpus

Compute the gap of publicdrive entries not yet ticked in `queue.md`:

```python
import json, re, pathlib, collections
m = json.loads(pathlib.Path("ask_jojo_raw/manifest.json").read_text())
queued = set(re.findall(
    r"^\s*-\s*\[[ xX]\]\s+(\S+)",
    pathlib.Path("ask_jojo/docs/compile/queue.md").read_text(),
    re.MULTILINE,
))
pd = sorted(k for k, e in m["entries"].items() if e["source_type"] == "publicdrive" and k not in queued)
print(f"Public Drive entries to absorb: {len(pd)}")

def top(eid, m=m):
    sid = m["entries"][eid]["source_id"]
    return sid.split("/", 1)[0] if "/" in sid else "<root>"
tops = collections.Counter(top(k) for k in pd)
for t, n in tops.most_common(): print(f"  {n:>5}  {t}")
```

Drill one more level (`source_id.split("/")[1]`) for any top-folder above ~500 entries. Sample 3-5 raw `.md` files from each major cluster to gauge content type (decisions, methodology, reports, ephemera, instrument output, software cache, deprecated material).

For each cluster, classify as **absorb** (real wiki signal) or **skip** (bulk evidence, software cache, duplicates already in sharepoint, instrument-output crumbs the converter handled but with low signal density, single-person workspaces). Skip-pool aggressively: a 14,000-entry batch is already hard to absorb cleanly; cutting the noise floor matters.

### Stage 3 — Author the publicdrive batches in `queue.md`

Two layout options exist in the existing queue:

- **Single-mega-batch with named subsections** (Batch 23 style — one `## Batch N` heading, multiple `### Cluster name (count)` subsections, theme paragraph above each). Use this when the clusters share enough framing to benefit from one shared theme paragraph and the absorb work fits inside one logical unit.
- **Many-small-batches** (Batches 1–22 style — one `## Batch N` heading per topical cluster, ~10–50 entries per batch, one theme paragraph per batch). Use this when you'd rather make Prompt 2's batch-loop visible at the queue level — the operator can stop after any single batch and inspect.

For Public Drive, prefer **many-small-batches**: the corpus has heterogeneous content (SOPs, instrument procedures, group meetings, archived projects, decision PDFs, departed-employee desktops) and each cluster wants distinct framing. Keep each batch under ~150 absorb-pool entries; subdivide a cluster if it exceeds that. Skip-pool entries can pile up in a single trailing batch (`## Batch K — Public Drive skip-pool`) or be distributed at the foot of each topical batch — match Batch 22's "skip-pool restore" precedent.

For each new batch, the heading block is:

```markdown
## Batch N — <one-line descriptive name>

**Theme:** <one paragraph: what's in this batch, what wiki output shape to expect, why these entries cluster together. Cite the corpus subdirectory or naming convention that defines the cluster. End with a one-sentence forecast: "Expected outputs: ~<N> <type> pages anchored on <topic>, plus <other-type> updates on existing pages.">

**Connector:** publicdrive
**Access level:** all_fte  *(default for Public Drive; adjust per-cluster if a subtree is access-restricted)*

- [ ] <publicdrive_entry_id>
- [ ] <publicdrive_entry_id>
- ...
```

Skip-pool entries inside a batch are pre-ticked with a comment explaining why:

```markdown
- [x] <publicdrive_entry_id>  <!-- skip: instrument-cache, no narrative content -->
```

Insert all the new `## Batch N` blocks **before** the `## Backlog — not yet batched` heading and **after** the last existing batch (currently Batch 23). Number them starting from 24.

### Stage 4 — Verify and commit

After all batches are authored, verify:

- Every `publicdrive` manifest ID appears exactly once in `queue.md` (either as `- [ ]` to absorb or `- [x] ... <!-- skip: ... -->` to skip-pool).
- No duplicates with prior batches (the gap computation already enforced this; double-check by re-running the gap script and asserting `len(pd) == 0`).
- Theme paragraphs cite the Nurix subdirectory or naming convention each cluster lives in.
- Heading numbering is contiguous (Batch 24, 25, 26, ... no gaps).

Commit `queue.md` in `ask_jojo/`. Use the lock-cleanup snippet first. **Stage only `docs/compile/queue.md`** — `ask_jojo` may have unrelated modified files (e.g. `ops/scheduler/Run-ScheduledSync.ps1`) that must not be added.

Commit message:
```
absorb(protein-sciences): Batches 24–<K> queue authored — Public Drive coverage

<one paragraph summarizing absorb-pool vs skip-pool counts and the
top-level cluster structure of the Public Drive>

Batch 24: <name> (<N> entries)
Batch 25: <name> (<N> entries)
...

Co-Authored-By: Claude Sonnet 4.6 via Cowork <noreply@anthropic.com>
```

Use the author override (`git -c user.email='cowork@anthropic.com' -c user.name='Cowork' commit ...`).

### Done conditions

Stop and report when:
- Manifest is rebuilt and committed in `ask_jojo_raw/`.
- Queue has all publicdrive entries accounted for (open or skip-tagged).
- Queue commit landed in `ask_jojo/`.
- No publicdrive walk is still running on the laptop (kill the scheduled task before pushing — `schtasks /End /TN "JojoBot-publicdrive"`).

Tell the operator the push commands they need to run from the laptop:
```
cd C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\ask_jojo_raw && git push
cd ..\ask_jojo && git push
```

### === PASTE ABOVE ===

---

## Prompt 2 — Absorb every Public Drive batch (loop until queue is empty)

Run this after Prompt 1 lands. It claims the first publicdrive batch with any open boxes, absorbs it per `compile-prompt.md`, commits, runs a 15-entry checkpoint when due, then claims the next batch, until every publicdrive batch in `queue.md` is fully ticked. Re-pasting the prompt in a fresh Cowork session resumes from wherever the previous session stopped.

### === PASTE BELOW ===

You are running the Phase 2 absorb loop against the Public Drive corpus. This session takes batches one at a time from `ask_jojo/docs/compile/queue.md`, runs the canonical absorb loop on each, commits, and moves to the next. Sessions are resumable: every batch's commit lands before the next begins, so a session that runs out of context can be replaced by a fresh paste of this prompt.

**Read first** (full files, in this order):

1. `ask_jojo/docs/compile/compile-prompt.md` — the canonical single-batch absorb prompt. **Treat its `=== PASTE BELOW ===` block as the contract for each batch.** The prompt below wraps it in a loop; it does not replace it.
2. `ask_jojo/schema/CLAUDE.md` — absorb loop (§2), 15-entry checkpoint (§3), anti-cramming / anti-thinning (§5), citation discipline (§6), contradictions (§7), commit messages (§9), what you may not do (§11). If anything below contradicts §1–§13 of `schema/CLAUDE.md`, the constitution wins; flag the conflict and stop.
3. `ask_jojo_wiki/SCHEMA.md` — frontmatter schema, page-type table, citation format, length targets (§9).
4. `ask_jojo/schema/taxonomy.yaml` — directory taxonomy. If a batch needs a directory not in the taxonomy, propose the addition in the same commit; do not force-fit.
5. `ask_jojo_wiki/_index.md` and `ask_jojo_wiki/_backlinks.json` — current wiki state.

### The loop

```
while True:
    1. Find the first ## Batch N in queue.md (under the publicdrive
       Public Drive coverage block) whose entries include at least one
       open `- [ ]` line. If none exist, STOP and report "publicdrive
       queue empty"; do not proceed past this point.
    2. Run the absorb loop from compile-prompt.md against that batch,
       end-to-end:
         - For each open entry: read raw, read affected wiki pages,
           plan, write, verify, link, tick the box.
         - Skip-tag entries that turn out to be unreadable / over-redacted
           with `- [x] <id>  <!-- skip: <one-line reason> -->`.
         - Use a fresh subagent (Task / Agent) per page-write where
           the per-page plan calls for it; spawn at most 5 in parallel
           per the schema/CLAUDE.md absorb-loop step 4 contract.
    3. Update _index.md (regenerate from frontmatter — do not append by
       hand; that's how Batches 23.3 and 23.4 drifted). Use the
       _index.md rebuild script in queue.md's preamble (or, if it's
       not there, walk ask_jojo_wiki/, group by frontmatter `type`,
       sort lexicographically by `title`, write the catalog).
    4. Regenerate _backlinks.json (pure Python, no LLM) by walking
       every wiki .md, extracting `[[slug|...]]` and `related:` entries,
       and writing `{ slug -> sorted list of pages linking to it }`.
    5. Commit ask_jojo_wiki/ with the constitutional message form:
         absorb(protein-sciences): N pages touched, M created
       Body lists each touched page path with (created)/(updated).
       (Subject form is from schema/CLAUDE.md §9 — match it exactly.)
    6. Commit ask_jojo/ with the queue tick:
         absorb(protein-sciences): Batch N queue tick
       Stage only docs/compile/queue.md. Do not touch the unrelated
       modified files in ask_jojo/.
    7. **Checkpoint cadence.** Track entries-absorbed across batches
       *within this session* in a counter. After every 15 absorbed
       entries (NOT every 15 batches), pause the outer loop and run
       the full 15-entry checkpoint per schema/CLAUDE.md §3:
         a. Rebuild _index.md (already step 3 above; redo if drifted).
         b. Rebuild _backlinks.json (already step 4 above; redo).
         c. Bloat check: pages past SCHEMA.md §9 "consider splitting"
            threshold get flagged for the next breakdown pass — write
            the flag list to ask_jojo_wiki/_needs_review.md and commit.
         d. Stub audit: pages with frontmatter `status: stub` that have
            accumulated content past the §9 stub threshold get
            promoted (status -> active); flag the rest for review.
         e. Orphan scan: pages with zero incoming wikilinks AND no
            useful aliases get appended to _needs_review.md.
         f. Schema-version drift: pages whose schema_version trails the
            current value get migrated.
         g. Taxonomy drift: any directory created ad-hoc since the
            last checkpoint that isn't in schema/taxonomy.yaml gets
            either added there or flagged for the operator.
         h. Commit the checkpoint output as its own commit:
              checkpoint: post-batch-N <one-line summary>
            Body: counts and any flagged items. Single commit.
    8. Continue from step 1.
```

**Subagent discipline (per `schema/CLAUDE.md` §2 absorb-loop step 4 and §12 "fresh context").**
- Each per-page plan instruction goes to a fresh subagent with only the inputs it needs: the plan instruction for that page, the existing page body (if any), the relevant section of the source entry, and up to three neighbor pages.
- Verify is a separate, cheaper subagent: frontmatter valid? wikilinks resolve? every paragraph cites at least one source in frontmatter `sources:`? confidence reasonable per §5? On any failure, requeue to the writer (max 2 retries) before flagging for human review.
- Per-batch parallelism: at most 5 page-writes in parallel. Wider parallelism risks `_index.md` / `_backlinks.json` write conflicts.

**Anti-patterns to actively resist (per `schema/CLAUDE.md` §5 and `PLAN.md` §6 Phase 2 anti-patterns).**
- *Anti-cramming.* If you're about to add a third paragraph on a sub-topic to an existing article, that sub-topic almost certainly deserves its own page. Create it, link from the original, move the accumulated material over.
- *Anti-thinning.* Every time you touch a page, it should get meaningfully richer. A stub with three vague sentences when four entries also mentioned the topic is a failure. Pull material from every entry in the batch's plan that mentioned the topic, not just the one that triggered creation.

**Stop conditions** (priority order):

1. *Constitutional conflict.* This prompt and `schema/CLAUDE.md` disagree. Surface verbatim, stop.
2. *Queue empty.* No publicdrive batch has any open `- [ ]` line. Report and stop.
3. *Checkpoint flagged something blocking.* If the bloat / stub / orphan / taxonomy-drift checks surface a problem the loop can't auto-resolve, commit the checkpoint anyway, then stop and surface to the operator.
4. *Source unreadable.* Skip-tag and continue (do not stop the loop on a single bad entry).
5. *Context running out.* Self-monitor: when token usage suggests fewer than ~30k tokens remain in this session, finish the current batch's commit cycle, then stop cleanly and tell the operator to re-paste this prompt in a new session.

**Do not** push, run lint, write to `ask_jojo_raw/`, or modify schema files (except `schema/taxonomy.yaml` for legitimate directory additions and `docs/compile/compile-prompt.md` if you find a tightening — propose, don't silently edit).

Begin from the first publicdrive batch with an open `- [ ]` line in `queue.md`.

### === PASTE ABOVE ===

---

## Prompt 3 — Audit and review the absorb output

Run this once Prompt 2 reports `publicdrive queue empty`. It runs a hard pass over the wiki + queue + manifest invariants, surfaces drift, and fix-forwards what's mechanically fixable. The output is a single audit commit + a plain-English report the operator can decide to act on (or sign off).

### === PASTE BELOW ===

You are running an audit pass before the Phase 2 engineering sub-deliverables begin. This session does not absorb. It walks the wiki, the queue, and the manifest, and it asks: did the Cowork-driven absorb loop produce output consistent with the Phase 2 contract in `PLAN.md` §6 and the constitution in `schema/CLAUDE.md`? Output is one commit (`audit:` prefix) summarizing what was checked, what was found, and what was fix-forwarded.

**Read first.**

- `ask_jojo/PLAN.md` §6 Phase 2 — exit criterion in particular.
- `ask_jojo/schema/CLAUDE.md` §3 (checkpoint), §5 (anti-patterns), §6 (citation), §7 (contradictions), §11 (what you may not do).
- `ask_jojo_wiki/SCHEMA.md` §6 (citation format), §7 (contradiction handling), §9 (length targets).

**Audit checks.**

Run each check; produce a structured report (markdown table, one row per check). For each check, also fix-forward where it's mechanical (rebuild a stale index file, retroactively skip-tag a queue entry, etc.). Where the check finds a quality problem that needs human judgment, write to `ask_jojo_wiki/_needs_review.md` (or `ask_jojo/docs/compile/audit-<date>.md`) and flag it; do not auto-resolve.

1. **Queue truthfulness.** Every publicdrive manifest ID is either `- [x]` (absorbed) or `- [x] ... <!-- skip: ... -->` (skip-pooled). No open boxes. No duplicates with onedrive / sharepoint batches. Run the gap script from Prompt 1; assert `len(unticked) == 0`.

2. **Manifest ↔ raws integrity.** Every `manifest.json` entry has a corresponding `.md` file at the recorded `path`, and each file's content sha256 (canonical, per `packages/jojo_connectors_common/hashing.py:canonical_sha256`) matches the manifest's `sha256`. Surface any drift; do not patch raws (the raw layer is immutable per `schema/CLAUDE.md` §11).

3. **Wiki ↔ index consistency.** Every `.md` page on disk under `ask_jojo_wiki/` (excluding `_*.md`, `README.md`, `SCHEMA.md`) appears in `_index.md`, with the title and confidence pulled from frontmatter. If `_index.md` is stale, regenerate it (the rebuild script lives in `queue.md` preamble; or walk the wiki, group by `type`, sort by `title`).

4. **Backlinks integrity.** `_backlinks.json` is consistent with the live wikilink graph: every `[[slug|...]]` reference and every `related:` entry across the wiki has the source page listed under that slug's bucket. Regenerate if stale.

5. **Frontmatter conformance.** Every wiki page has the required fields per `SCHEMA.md` §3: `schema_version`, `corpus`, `confidence`, `type`, `title`, `aliases` (may be empty list), `sources` (non-empty), `created`, `last_updated`, `last_reviewed`. Pages missing required fields go to `_needs_review.md`.

6. **Citation density.** Sample 30 random wiki pages. For each, count paragraphs vs cited paragraphs. Per `schema/CLAUDE.md` §6, every paragraph must cite at least one source in `sources:`. Surface any page where >10% of paragraphs are uncited; flag in `_needs_review.md`.

7. **EXTRACTED vs INFERRED labels.** Sample 20 random pages. Look for INFERRED claims that lack hedging language ("suggests", "implies", "consistent with") or a `confidence: medium` / `low` frontmatter. Anti-pattern: an INFERRED claim promoted to EXTRACTED by silently dropping the hedges (`schema/CLAUDE.md` §6).

8. **Contradiction surfacing.** Search for pages whose frontmatter has `status: contradictory` or where the body uses words like "however", "but", "in contrast" against multiple cited sources. Confirm the contradiction handling follows `SCHEMA.md` §7's four rules. Flag silent contradictions (one source picked over another without note).

9. **Anti-cramming detection.** For each `programs/`, `targets/`, and `methods/` page over 1500 words (per `SCHEMA.md` §9 "consider splitting"), check whether a subsection is duplicated as a paragraph on multiple pages — that's a sign cramming happened in one place that thinning would have surfaced as a missing page. Flag candidates.

10. **Anti-thinning detection.** For each batch in `queue.md`, count distinct pages created vs entries absorbed. A batch where ~all entries created their own short stub page and nothing was aggregated is the thinning anti-pattern. Surface candidates.

11. **Wikilink integrity.** Every `[[slug|...]]` resolves to a page that exists. Surface dangling links; if a dangling link is to a page that obviously should exist (program / target / method named in the source corpus), flag for creation.

12. **Style violations.** Grep the wiki for em-dashes (`—`), peacock words (the SCHEMA.md §4 list — `comprehensive`, `robust`, `cutting-edge`, `state-of-the-art`, `seamless`, `powerful`, `leveraging`, `meticulously`, `delve`, `tapestry`, `landscape`), first-person plural (`we`, `our`), and editorial framing (`importantly`, `crucially`, `clearly`, `it is worth noting`). Each grep returns a count and a sample. High counts = the absorb loop drifted on style.

13. **Date format conformance.** All dates in wiki pages are ISO `YYYY-MM-DD` per `schema/CLAUDE.md` §4. Surface any `Mar 10, 2025` / `3/10/25` / similar.

14. **Quote budget.** Per `schema/CLAUDE.md` §4 "Quote budget", no page has more than three direct quotes, each ≤ two sentences. Surface violators.

15. **Schema-version drift.** Every page's `schema_version` matches the current `SCHEMA.md` version. If the schema bumped during absorb, list the lagging pages.

**Output.**

Two artifacts:

1. A new file `ask_jojo/docs/compile/audit-<YYYY-MM-DD>.md` with: the table of checks (status: pass / fail / fixed-forward / flagged-for-human), the count and sample for each, and a one-paragraph executive summary.
2. Updates to `ask_jojo_wiki/_needs_review.md` with each flagged page, the check that flagged it, and a one-line description of what to fix.

**Commits.**

- One commit in `ask_jojo_wiki/` for any regenerated `_index.md` / `_backlinks.json` / `_needs_review.md`. Subject: `audit: post-publicdrive sweep — N pages flagged, indexes regenerated`. Body: per-check counts.
- One commit in `ask_jojo/` for the audit report. Subject: `audit(phase-2): post-publicdrive sweep`. Body: executive summary + a "blockers vs nits" split.

Use the lock-cleanup snippet and the author override.

**Stop conditions.**

- *Hard fail* (stop and surface, do not auto-fix): manifest-vs-raws sha256 drift; pages with no `sources:` field at all; queue with open `- [ ]` lines.
- *Soft fail* (auto-fix-forward, log in audit report): stale `_index.md` or `_backlinks.json`; missing skip-tag rationale; minor frontmatter omissions on otherwise-valid pages.
- *Flag-for-human* (write to `_needs_review.md`, do not block): style violations; bloat / stub / orphan candidates; suspected anti-cramming or anti-thinning; INFERRED claims missing hedges.

Tell the operator at the end: how many checks passed, how many fixed-forward, how many need human review, and (if the hard-fail list is empty) green-light Prompt 4.

### === PASTE ABOVE ===

---

## Prompt 4 — Build the `packages/jojo_compile/` engineering deliverables

Run this after Prompt 3 returns a clean audit. This session implements the Phase 2 *engineering* deliverables: the code that automates what Cowork has been doing manually. Sub-deliverables are spelled out in `PLAN.md` §6 Phase 2 — do not redefine them in this session, build them.

### === PASTE BELOW ===

You are implementing the Phase 2 compile-pipeline engineering deliverables. The Cowork-driven manual absorb loop has filled the wiki; now build the code that automates it. After this session, `packages/jojo_compile/` contains the modules listed in `PLAN.md` §6 Phase 2 deliverables, the absorb loop runs end-to-end from the CLI on a synthetic corpus with golden-file regression tests, and the pipeline implements the four-step contract (Ingest → Absorb → Write → Verify) with checkpoint discipline and the cross-walk to the reference projects already noted in `PLAN.md`.

**Read first** (full files):

- `ask_jojo/PLAN.md` §6 Phase 2 — particularly the "Four-step pipeline per entry" subsection, "Anti-patterns designed-against in the prompts" subsection, "Checkpoint discipline" subsection, "Cross-walk" subsection, "Deliverables" subsection, and "Exit criterion" subsection. **Every paragraph below maps to one of those subsections.**
- `ask_jojo/schema/CLAUDE.md` — the absorb loop spec (§2), the 15-entry checkpoint spec (§3), the anti-pattern spec (§5), citation discipline (§6).
- `ask_jojo_wiki/SCHEMA.md` — frontmatter schema (§3), citation format (§6), contradiction rules (§7), length targets (§9).
- `ask_jojo/packages/jojo_connectors_common/manifest.py` — Manifest class that the compile pipeline consumes.
- `ask_jojo/packages/jojo_ingest/driver.py` and `ask_jojo/packages/jojo_ingest/cli.py` — for shape consistency (compile CLI mirrors ingest CLI).
- `ask_jojo/docs/compile/compile-prompt.md` — the canonical absorb prompt that the `prompts/absorb/*.md` library should distill from.
- `ask_jojo/docs/ADR/0010-compile-via-cowork-while-api-pending.md` — the constraint shape the API path takes when implemented.

**Module layout** (per `PLAN.md` §6 Phase 2 deliverables; create files at these paths):

```
packages/jojo_compile/
├── __init__.py
├── cli.py            # `python -m jojo_compile absorb [--range last-30-days|all|<manifest>]` and `rebuild-index`, `reorganize`, `breakdown`
├── absorb.py         # outer loop: pulls unabsorbed entries, runs the four-step pipeline per entry
├── plan.py           # step 2: reads entry + index + neighbors → emits structured absorb-plan JSON
├── write.py          # step 3: per-page subagent, parallel batch of 5, fresh-context-per-page
├── verify.py         # step 4: per-page check (frontmatter, wikilinks, citations, confidence)
├── link.py           # link step + _backlinks.json rebuild (pure Python, no LLM)
├── checkpoint.py     # 15-entry checkpoint per schema/CLAUDE.md §3
├── breakdown.py      # bloat-driven page splitting
├── reorganize.py     # multi-page rewrites (taxonomy drift fixups)
├── prompts/
│   ├── plan.md       # absorb-planner subagent prompt
│   ├── write.md      # page-writer subagent prompt
│   ├── verify.md     # verifier subagent prompt
│   └── breakdown.md  # breakdown subagent prompt
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   │   └── fake-nurix/        # synthetic 8-entry corpus (raw .md inputs + golden wiki output)
│   ├── test_plan.py
│   ├── test_write.py
│   ├── test_verify.py
│   ├── test_link.py
│   ├── test_checkpoint.py
│   └── test_absorb_e2e.py     # full four-step pipeline against fake-nurix
└── README.md
```

Add `packages/jojo_compile` to the `[tool.hatch.build.targets.wheel]` packages list in `pyproject.toml`.

**Four-step pipeline contract** (each step a separate function with a clean signature; subagents called via `Anthropic SDK / Claude Agent SDK` against the model from `schema/CLAUDE.md` §10's routing table):

1. **Ingest → normalized entry.** Already done in Phase 1; the compile pipeline consumes `Manifest.entries` and reads the corresponding raw `.md` files. Add a chunker for entries whose body exceeds the absorb-planner model's context — it lives in `absorb.py:_load_entry_chunks` and uses v1.0's ChromaDB or an in-process equivalent for similarity-keyed chunk retrieval. The compile config holds the chunk threshold (default: 60k tokens of body text).

2. **Absorb → absorb-plan JSON.** `plan.py:plan_for_entry(entry, index, neighbors) -> AbsorbPlan`. Sonnet reads the entry plus `_index.md` plus a short list of closely-related pages (keyword + alias overlap, top 12 candidates). Output is a strict-typed `AbsorbPlan` dataclass: `pages: list[PagePlan]` where each `PagePlan` is `(slug, action: 'create'|'update'|'no-op', sections_to_add: list[str], rationale: str)`. **Plan budget cap: ≤12 page touches per entry.** A plan over budget pauses the entry for human review per `PLAN.md` §6 Phase 2 — this is the anti-cramming guard rail.

3. **Write → individual page updates.** `write.py:write_page(plan_instruction, current_body, source_section, neighbors) -> str`. Per-page subagent with a fresh context: only the four inputs above. Returns the new page body + frontmatter. Parallel batch size: 5. Commits happen at the batch boundary, not per-page (matches `compile-prompt.md`'s atomic-batch contract).

4. **Verify → pass/fail per page.** `verify.py:verify_page(path) -> VerifyResult` with `passed: bool, failures: list[VerifyFailure]`. Failures requeue to `write.py` (max 2 retries; tracked in `absorb.py:_retry_count`). On final failure, the page goes to `_needs_review.md` (do not block the rest of the batch).

**Checkpoint discipline** (per `schema/CLAUDE.md` §3 and `PLAN.md` §6 Phase 2 "Checkpoint discipline"). After every 15 absorbed entries, `checkpoint.py:run_checkpoint()` does, in order:
1. Rebuild `_index.md` from frontmatter (pure Python).
2. Rebuild `_backlinks.json` from wikilinks + `related:` (pure Python).
3. New-article audit: count pages created in the last 15 entries; zero means cramming, flag.
4. Quality audit: pick 3 most-recently-touched pages, Opus re-reads each end-to-end, asks "does this read like a coherent article or a chronological dump?" and rewrites failures.
5. Bloat check: pages past `SCHEMA.md` §9 split threshold flagged for `breakdown.py`.
6. Tombstone sweep: superseded articles move to `archive/` with a `redirect_to:` field.

Checkpoint is a separate commit per `schema/CLAUDE.md` §9, prefix `checkpoint:`.

**Anti-patterns** (per `PLAN.md` §6 Phase 2 "Anti-patterns designed-against"). Encode both into the planner and writer prompts:
- *Anti-cramming.* The planner prompt says verbatim: "If you are about to add a third paragraph on a sub-topic to an existing article, that sub-topic almost certainly deserves its own page. Create it, link from the original, and move the accumulated material over."
- *Anti-thinning.* The writer prompt says verbatim: "Every time you touch a page, it should get meaningfully richer. A stub with three vague sentences when four other entries also mentioned the topic is a failure. Pull material from every source in the absorb-plan that mentioned this topic, not just the one source that triggered creation."

Add unit tests that lint the prompt files for these strings — if a future commit silently drops them, the test fails.

**Cross-walk** (the four reference projects from `PLAN.md` §6 Phase 2 "Cross-walk"). Document in `packages/jojo_compile/README.md` how each maps:
- Farzaa's `/wiki absorb` loop + checkpoint cadence + anti-patterns + Wikipedia-flat tone — adopted wholesale; cite the source skill in the README.
- Karpathy's "single source touches 10–15 wiki pages" — encoded as the 12-page plan-budget cap.
- Arscontexta's Record → Reduce → Reflect → Reweave → Verify → Rethink — renamed Ingest → Absorb → Write → Verify (matches `PLAN.md` §6 Phase 2 four-step naming).
- Arscontexta's fresh-context-per-subagent — every plan, every page-write, every verify is its own subagent call with clean context (no shared session state).

**CLI** (per `PLAN.md` §6 Phase 2 deliverables): `python -m jojo_compile absorb [--range last-30-days|all|<manifest>]`, `rebuild-index`, `reorganize`, `breakdown`. Mirror `jojo-ingest`'s argparse style. Wire entry points in `pyproject.toml` next to `jojo-ingest`.

**Tests** (per `PLAN.md` §6 Phase 2 deliverables — golden-file tests):
- `tests/fixtures/fake-nurix/` is a hand-curated synthetic corpus: 8 raw `.md` entries spanning 3 programs, 2 targets, 1 method, 1 piece of equipment. Authored to surface both anti-patterns: two entries on the same target (anti-thinning bait), one entry sprawling across a target + a method + a program (anti-cramming bait).
- `tests/fixtures/fake-nurix-expected/` is the golden wiki: ~8 pages with the right cross-links and citations. Sized so a human can hold it in their head while debugging a regression.
- `test_absorb_e2e.py` runs the full four-step pipeline against `fake-nurix/`, diffs the output against `fake-nurix-expected/`. Failure prints a side-by-side diff. **Use a `mock_anthropic` fixture** for unit/CI runs (no API calls); flag a `--live` run for manual exit-criterion validation.
- Each step has its own focused tests (`test_plan.py` etc.) with mocked LLM responses for the inputs you care about.

**Linting and CI.** Add a `lint` job to the existing CI config (or scaffold one) that runs `ruff check`, `pytest`, and a "constitutional lint" pass that asserts the prompt files contain the anti-pattern strings verbatim. On every PR.

**Commits** (one per logical unit; each at the constitutional commit form):
1. `feat(compile): scaffold packages/jojo_compile (cli, absorb, plan, write, verify, link, checkpoint stubs)`
2. `feat(compile): four-step pipeline core (plan / write / verify / link)`
3. `feat(compile): 15-entry checkpoint per SCHEMA.md §3`
4. `feat(compile): breakdown + reorganize`
5. `feat(compile): prompt library (plan / write / verify / breakdown)`
6. `test(compile): fake-nurix fixture + golden-file e2e harness`
7. `feat(compile): wire CLI entry points + pyproject packaging`
8. `docs(compile): cross-walk + README + ADR update`

Use the author override and lock-cleanup snippet for each.

**Stop conditions.**

- *Constitutional conflict.* This prompt and `schema/CLAUDE.md` or `PLAN.md` §6 Phase 2 disagree. Surface verbatim, stop.
- *Test failure.* Any commit's pytest run leaves a red test you can't trace to a known limitation. Stop and report.
- *Time-or-context exhaustion.* If a session can't complete all eight commits, finish the in-progress commit cleanly and report which commits are landed and which remain.

Do not push. Do not run a `--live` end-to-end against the real corpus from this session — that's Prompt 5's job.

### === PASTE ABOVE ===

---

## Prompt 5 — Phase 2 exit-criterion review

Run this last. It reads the Phase 2 exit criterion from `PLAN.md` §6, runs the live compile pipeline against the real `ask_jojo_raw/` corpus on a fresh `ask_jojo_wiki/` clone, and writes the exit-evidence document that updates `docs/v2_status.md`.

### === PASTE BELOW ===

You are running the Phase 2 exit-criterion review. The compile pipeline now exists in `packages/jojo_compile/`; the wiki has the Cowork-absorbed corpus from Prompts 2-3. This session's job is to (a) confirm the four-step pipeline runs end-to-end against the real corpus, (b) score the current wiki against `PLAN.md` §6 Phase 2's exit criterion, and (c) write the Phase 2 exit-evidence document and flip the phase status in `docs/v2_status.md`.

**Read first.**

- `ask_jojo/PLAN.md` §6 Phase 2 — exit criterion at the bottom of the section. The exit text is authoritative.
- `ask_jojo/docs/phase-1-exit-evidence.md` — the precedent. This session's output should be `docs/phase-2-exit-evidence.md` in the same shape: gates table, per-gate evidence, links to validation reports.
- `ask_jojo/docs/v2_status.md` — the living phase tracker. The Phase 2 row's `Exit-criterion met` cell gets the date when this session is done.
- `ask_jojo/schema/CLAUDE.md` §6 (citation), §11 (forbidden moves) — used to score the wiki.

### Exit-criterion gates (from `PLAN.md` §6 Phase 2)

> From a fresh `ask_jojo_raw/` of 200+ Protein Sciences docs, a full compile produces a wiki that passes:
> 1. Every page has `sources`.
> 2. `_index.md` lists every page with aliases.
> 3. `_backlinks.json` matches manual spot-check.
> 4. ≥3 domain reviewers judge the top-10 pages "accurate and useful."
> 5. <5% of pages need immediate human intervention.
> 6. The v1.0 chat path still works.
> 7. Query still uses v1.0 RAG (that's Phase 4).
> 8. The Protein Sciences corpus scope-expansion review (§4 D12) can now begin.

Decompose into measurable checks; produce a `phase-2-exit-evidence.md` with one section per gate.

### Stage 1 — End-to-end live run

Run `python -m jojo_compile absorb --range all --raw ../ask_jojo_raw --wiki ../ask_jojo_wiki-test` (where `ask_jojo_wiki-test` is a fresh sibling clone — do NOT compile into the live `ask_jojo_wiki/` for this validation; we want to compare the freshly-compiled output against the Cowork-absorbed wiki). Time the run. Capture stdout/stderr to `ops/validation/reports/phase-2-live-compile-<YYYYMMDD>.log`. Confirm:

- Exit code 0.
- Total entries absorbed = total publicdrive + onedrive + sharepoint manifest entries minus the queued skip-pool.
- Plan-budget violations (>12 pages touched) flagged but not blocking.
- Verify failures (after retries) below 5% of pages touched.

### Stage 2 — Per-gate scoring

For each gate above, run a check, log the count, and decide pass / fail / partial. Fix-forward where mechanical (regenerate `_index.md`, fix a single missing-source-list page); flag for human where it isn't (a domain reviewer's judgment cannot be auto-passed).

Gate 4 ("≥3 domain reviewers judge top-10 pages accurate and useful") cannot be auto-passed — write a `docs/phase-2-domain-review-checklist.md` with the top-10 pages (chosen by frontmatter `confidence: high` + most incoming wikilinks), a rubric, and the names of the three reviewers (Mateo Sr., the Protein Sciences PI, the operator). Mark the gate "pending review."

Gate 5 ("<5% of pages need immediate human intervention") = (pages flagged in `_needs_review.md` ÷ total pages). Pass if <5%, partial if 5–10%, fail if >10%.

Gate 6 ("v1.0 chat path still works") = run the v1.0 query suite from `precedent/` against the v1.0 ÄKTA / UNICORN corpus, confirm answer quality unchanged from baseline. Document.

Gate 7 ("Query still uses v1.0 RAG") = read `packages/jojo_qa/`'s wiring (or absence of); confirm the v2 query path is not yet active. This is a no-change confirmation.

Gate 8 ("scope-expansion review can now begin") = check that `docs/scope-expansion/` (or wherever §4 D12 lives) is scaffolded with the inputs the review needs: per-page confidence histogram, per-domain coverage map, top remaining sources unabsorbed.

### Stage 3 — Write the exit evidence

Author `ask_jojo/docs/phase-2-exit-evidence.md` matching the structure of `phase-1-exit-evidence.md`:

```markdown
# Phase 2 Exit-Criterion Evidence

**Last updated.** <YYYY-MM-DD>

This doc captures the observational evidence that Phase 2 ("Wiki Compile")
has met the exit criterion defined in `PLAN.md` §6 Phase 2 and
`docs/v2_status.md`. ...

## Exit criterion (from PLAN.md §6 Phase 2)

> [verbatim quote of the exit criterion]

## Gates table

| # | Gate | Status | Evidence |
| - | --- | --- | --- |
| 1 | Every page has `sources:` | 🟢 / 🟡 / 🔴 | <count and pointer to validation report> |
| ... |

## Evidence per gate

### Gate 1 — Every page has `sources:`
<plain-prose evidence with counts and links>

...
```

### Stage 4 — Update `v2_status.md`

In `docs/v2_status.md`, set the Phase 2 row's `Exit-criterion met` cell to today's date if every gate passed (or every fail-able gate passed, with Gate 4's domain review marked "pending"); otherwise leave it blank and add a Notes block with the failing gate(s). Update the Phase 2 status emoji accordingly (🟢 if exited, 🟡 if pending domain review, 🟡 / 🔴 if blocking gate failed).

### Commits

- `ask_jojo/`:
  - `docs(phase-2): exit-criterion evidence` (the new `phase-2-exit-evidence.md`)
  - `docs(v2): mark Phase 2 exited` (update `v2_status.md`)
  - `docs(phase-2): domain-review checklist for top-10 pages` (the reviewer rubric)
- `ask_jojo_wiki/`:
  - any fix-forward `_index.md` / `_backlinks.json` / `_needs_review.md` regeneration
  - subject `audit: phase-2 exit sweep — N pages flagged` if anything changed
- `ops/validation/reports/`:
  - `phase-2-live-compile-<YYYYMMDD>.log` (the live-run output)
  - `phase-2-gate-scoring-<YYYYMMDD>.json` (machine-readable per-gate counts)

Use the author override + lock-cleanup snippet on each.

### Stop conditions

- *Live compile crashes.* Stop; the engineering pipeline isn't ready. Surface the failure to the operator with stack trace + the Prompt 4 commit it traces back to.
- *Hard fail on a non-domain gate.* Stop; flag what failed; do not green-light Phase 2 exit.
- *Soft fail on domain review.* Phase 2 exit is provisional pending reviewers; report and stop. Don't auto-resolve domain judgment.
- *Clean pass.* Commit, push the operator the green light, end-of-Phase-2 done.

Tell the operator at the end: each gate's status, what to do next (push, kick off Phase 3 / Phase 4 work, schedule the domain review), and what (if anything) the operator should keep an eye on (pending reviewer, soft-fail gate, etc.).

### === PASTE ABOVE ===

---

## Change log

| Date | Change | Reason |
| --- | --- | --- |
| 2026-04-27 | v0.1 — initial five-prompt sequence for the Public Drive → Phase 2 exit cycle | Authored after the publicdrive walker fix (commit b9a2823) and the corpus-state reconciliation discovery (manifest.json was clobbered mid-save during the 2026-04-25 publicdrive run). |
