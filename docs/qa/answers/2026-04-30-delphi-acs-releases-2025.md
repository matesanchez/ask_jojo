---
question_id: q-004
question: "Walk me through the major Delphi ACS releases from inception through 2025 — what changed in each, and what was the major decision behind each scope?"
asked_by: mateo
asked_date: 2026-04-30
session_date: 2026-04-30
session_id: cowork-2026-04-30-004
route: wiki
route_decided_by: regex
candidate_slugs:
  - delphi
  - delphi-acs-scope
  - delphi-pre-acs-timeline
  - delphi-acs2024-1-release
  - delphi-acs2025-1-release
  - delphi-acs2025-2-release
  - delphi-acs2025-3-release
  - delphi-acs2024-1-uat-cycle
  - delphi-acs2025-1-uat-cycle
  - delphi-acs2025-2-uat-cycle
hops_followed:
  - delphi-acs2026-2-release
  - delphi-campaign-planning-v3-0-0
  - delphi-acs2022-sept-release
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: true
filed_back_path: ask_jojo_wiki/derived/2026-04-30-delphi-acs-release-narrative.md
schema_version: 0.1.0
---

## Answer

The Delphi platform is the Nurix internal software for [[delphi|campaign planning and protein production tracking]], structured as a two-module web application: Campaign Planning (CP) and Protein Production (PP). The "ACS" designation refers to **A**dvanced **C**onstruct **S**upport, the multi-year scope expansion that lets Delphi handle complex protein constructs beyond the simple monomer-with-tag base case. The scope itself was framed in 2020 [[delphi-acs-scope|delphi-acs-scope]], but the release stream that delivered it ran from late 2024 through 2026.

Before ACS, Delphi went through a Pre-ACS era covered in [[delphi-pre-acs-timeline|delphi-pre-acs-timeline]] (2020–2022) and a v3.0.0 release on 2022-11-28 that restructured the campaign-planning data model so buffers, supplements, tracers, and screen plans linked directly to the project rather than to a campaign version [[delphi-campaign-planning-v3-0-0|delphi-campaign-planning-v3-0-0]]. The v3.0.0 release resolved tickets DS-241, DS-294, and DS-292; it preceded ACS proper but is the structural foundation that ACS built on. The September 2022 ACS-prep release [[delphi-acs2022-sept-release|delphi-acs2022-sept-release]] is the pre-ACS bridge.

The ACS release sequence proper is captured in four release pages and three UAT-cycle pages in the wiki's `decisions/` directory. The numbering convention is `ACS<year>.<release-in-year>` so `ACS2024.1` is the first ACS release of 2024.

The first ACS release, [[delphi-acs2024-1-release|ACS2024.1]], landed alongside its [[delphi-acs2024-1-uat-cycle|ACS2024.1 UAT cycle]] and delivered the initial advanced-construct features that the [[delphi-acs-scope|ACS scope]] document had defined. The wiki page captures the release-specific scope decisions and ticket resolutions; the UAT-cycle page captures the test plan, the bugs surfaced during user-acceptance testing, and the scope-deferral decisions made when bugs were severe enough to push features into the next release. The relationship between release pages and UAT pages is general: every ACS release has a paired UAT cycle, the UAT cycle precedes the release, and the UAT page is where scope-decision artifacts (deferrals, must-have additions) are recorded.

The 2025 sequence is [[delphi-acs2025-1-release|ACS2025.1]], [[delphi-acs2025-2-release|ACS2025.2]], and [[delphi-acs2025-3-release|ACS2025.3]], with paired UAT cycles in [[delphi-acs2025-1-uat-cycle|ACS2025.1 UAT]] and [[delphi-acs2025-2-uat-cycle|ACS2025.2 UAT]]. The wiki notes each release's scope on its own page; the most consistent pattern across the 2025 releases is incremental expansion of construct types and tightening of the clone-biomass-protein registration data flow, with `ACS2025.2 UAT` being one of the bloat-flagged decision pages in `_needs_review.md` (168 lines, near the split threshold), which is a marker that this UAT cycle had unusually rich scope-decision content.

Beyond 2025, the wiki has a single 2026 release page, [[delphi-acs2026-2-release|ACS2026.2]]. The presence of a `.2` release without a `.1` is a known wiki-content gap rather than a Delphi-side anomaly — the absence of `delphi-acs2026-1-release.md` from the index suggests either that the 2026.1 release page was not yet absorbed at the 2026-04-29 checkpoint or that 2026.1 was a minor release that did not warrant its own decision page. INFERRED: the wiki's coverage of 2026 Delphi releases is incomplete relative to 2024–2025; a fresh absorb against the `delphi-campaign-planning-release-notes-prod-v3-0-0-1-pdf` and any newer release-notes raw entries would close the gap.

The "major decision" behind each release's scope is captured on a per-release basis rather than as a unifying narrative in any single wiki page. Reading the four release pages and three UAT pages together, the consistent shape is: the [[delphi-acs-scope|ACS scope]] document defined the multi-year ambition (advanced-construct support: complex stoichiometries, fusion proteins, paired domains, tags-and-cleavage), and each release page documents which scope items shipped that release and which deferred to the next. The UAT pages capture the *forcing functions* — the bugs and gaps surfaced under realistic user load that determined whether a scope item was production-ready or had to slip. This pattern is consistent from ACS2024.1 forward.

## Sources

- `delphi` — platform-level page; defines the two-module architecture and provides the v3.0.0 release detail. Source list ends 2025-07-02.
- `delphi-acs-scope` — primary scope-defining decision; the multi-year ambition.
- `delphi-pre-acs-timeline` — the 2020–2022 history that preceded ACS.
- `delphi-campaign-planning-v3-0-0` — the November 2022 release that restructured the data model.
- `delphi-acs2022-sept-release` — September 2022 pre-ACS bridge release.
- `delphi-acs2024-1-release` and `delphi-acs2024-1-uat-cycle` — first ACS release pair.
- `delphi-acs2025-1-release`, `delphi-acs2025-2-release`, `delphi-acs2025-3-release` — 2025 release sequence.
- `delphi-acs2025-1-uat-cycle`, `delphi-acs2025-2-uat-cycle` — 2025 UAT cycle pair (ACS2025.3 UAT cycle either does not exist or was not absorbed).
- `delphi-acs2026-2-release` — single 2026 release page; coverage gap on `delphi-acs2026-1-release` flagged.

## Confidence

Highest-confidence claims: (a) the two-module Delphi architecture (CP + PP) and the v3.0.0 data-model restructuring; (b) the existence of release-and-UAT pairs from ACS2024.1 forward.

Medium-confidence claim: the per-release scope summaries above. The wiki has a release page for each, but the answer's pattern-level synthesis ("incremental expansion of construct types and tightening of the clone-biomass-protein registration data flow") is INFERRED across multiple pages rather than EXTRACTED from any one. A reviewer with direct knowledge of the 2025 release notes would either confirm or refine this.

Lowest-confidence claim: the gap on `delphi-acs2026-1-release.md`. The wiki's `_index.md` lists `delphi-acs2026-2-release` but not `.1`. This could be a coverage gap in the absorb, a renamed release, or a minor release without its own page. Marked INFERRED.

The release pages and UAT pages do not disagree with each other; they cover different aspects of the same release events. The `delphi-acs2025-2-uat-cycle` page is bloat-flagged in `_needs_review.md` but bloat is a length issue, not a content-correctness issue.

## Follow-ups

1. Was there a `delphi-acs2026-1-release` that was either skipped, renamed, or absorbed under a different slug? A targeted absorb pass against any 2026.1 release-notes raw entry would close this gap.
2. Across the four ACS releases (2024.1, 2025.1, 2025.2, 2025.3), which scope items first appeared in the [[delphi-acs-scope|ACS scope]] document and which were added during execution? A cross-reference table would be a high-leverage `derived/` page.
3. The `delphi-acs2025-2-uat-cycle` page is bloat-flagged and may be ready for a breakdown pass — should some of its scope-decision content be promoted to its own decision page (e.g. "ACS2025.2 LASCEXPRTASK Mandatory Fields", which already exists as [[delphi-ds841-lascexprtask-mandatory-fields|delphi-ds841-lascexprtask-mandatory-fields]])?

## Filed back?

Yes. The cross-release narrative is novel synthesis worth promoting. Filed to `ask_jojo_wiki/derived/2026-04-30-delphi-acs-release-narrative.md` with `confidence: low` per `qa-prompt.md`. The next absorb checkpoint can decide whether to merge into `delphi-acs-scope` or promote to its own page (e.g. `decisions/delphi-acs-release-narrative.md`).

## Session notes

This question is the first answer in the seed-5 set that hits the file-back threshold (>200 words of novel synthesis). The synthesis is the cross-release narrative that no single wiki page contains; the individual release pages each cover one release in isolation. Worth adding a benchmark category for "synthesis-required" questions where the answer's correctness is gradable but no single source page can be cited as authoritative.

Two prompt-tightening notes:

1. The retrieval bundle's candidate slugs included three UAT pages and four release pages, but the answer ended up reading two more (`delphi-acs2026-2-release` and `delphi-campaign-planning-v3-0-0`) that the regex retrieval did not surface. The candidate-selection step should expand to include any slug whose `aliases` include "ACS" or "Delphi" rather than relying on title-substring match.
2. The wiki's pattern of release-and-UAT pairs is a useful structural feature for the graph-assisted retrieval path. The graph between a release page and its UAT page is a strong edge; questions that ask "what changed in release X" should hop from `delphi-acs<X>-release` to `delphi-acs<X>-uat-cycle` automatically. Worth noting in `packages/jojo_qa/graph.py` as a hop heuristic.
