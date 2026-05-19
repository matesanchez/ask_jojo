---
question_id: q-043
question: "What's the typical purification yield for NX-1607?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-043
route: v1
route_decided_by: regex
candidate_slugs: []
hops_followed: []
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: high
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**Router decision: `v1`.** This question is routed to the ÄKTA / chromatography legacy system (v1.0), not to the wiki. Routing is high-confidence.

The question contains the method keyword `purification yield`. Purification yield data — how much protein (or compound) is recovered per batch run — is a wet-lab production metric that lives in the v1.0 system. The keyword `purif` (from `purification`) is a primary v1-routing signal, regardless of whether a program-class keyword (`NX-1607`, a CBL-B inhibitor compound) appears in the same question. The wiki contains NX-1607 pharmacology, clinical status, and program history, but not purification yield data.

The session does not attempt to synthesize a purification yield from wiki content. The correct response is a routing slip directing the query to v1.0.

## Sources

_(none — v1 route bypasses the wiki)_

## Confidence

High on routing decision: `purification yield` unambiguously triggers `v1`. The NX-1607 program keyword does not override.

## Follow-ups

1. Does v1.0 have a per-batch purification yield log for NX-1607 synthesis runs?
2. Is there any wiki content in the CBL-B program pages that mentions compound batch yield as a CMC metric?

## Filed back?

No. This is a routing slip; no wiki content to file.

## Session notes

Router stress test: NX-1607 (program/compound keyword) + purification yield (method keyword). Expected behavior: `purif` wins over the compound name. This matches the backlog stub: "'purification yield for NX-1607' — `purif` keyword on program; route `v1`." The benchmark grader should confirm that the system does not return CBL-B wiki pages in response to this query. Compare to q-005 (ÄKTA + BTK), q-040 (ÄKTA + Pellino-1), q-041 (chromatography + CBL-B): same pattern, different program/keyword combination.
