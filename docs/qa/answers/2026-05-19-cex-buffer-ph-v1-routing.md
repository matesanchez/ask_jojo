---
question_id: q-046
question: "What's the typical buffer pH range for cation-exchange chromatography on a typical kinase?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-046
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

**Router decision: `v1`.** This question is routed to the ÄKTA / chromatography legacy system (v1.0). Routing is high-confidence.

The question contains the chromatography method keyword `cation-exchange chromatography` and the buffer/method keyword `buffer pH`. Both are primary v1-routing triggers. The qualifier `typical kinase` is a generic protein-class reference, not a Nurix program keyword — it does not create routing ambiguity toward the wiki. The wiki contains kinase target pages (IRAK4, ZAP-70, BTK), but none of them document cation-exchange chromatography buffer selection. Buffer pH guidance for a chromatography method lives in v1.0.

The session does not attempt to answer this question from the wiki. The correct response is a routing slip directing the query to v1.0.

## Sources

_(none — v1 route bypasses the wiki)_

## Confidence

High on routing decision: `cation-exchange chromatography` + `buffer pH` are unambiguous v1 signals. `typical kinase` is not a specific program keyword and does not override.

## Follow-ups

1. Does v1.0 have a general guide for CEX buffer pH selection (e.g., pI-based heuristics)?
2. Are there Nurix-specific CEX method files in v1.0 for kinase targets like IRAK4 or BTK?

## Filed back?

No. This is a routing slip; no wiki content to file.

## Session notes

Pure v1-routing test: `cation-exchange chromatography` + `buffer pH` + `typical kinase`. The backlog stub reads: "'buffer pH for cation-exchange chromatography on a typical kinase' — pure v1 question." This should be an unambiguous v1 route. The word `kinase` could theoretically point toward IRAK4 or ZAP-70 wiki pages, but `cation-exchange chromatography` + `buffer pH` clearly dominate. The benchmark should confirm that the system does not retrieve kinase target pages in response to this query.
