---
question_id: q-041
question: "Which chromatography column should I use for CBL-B purification?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-041
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

The question contains the method keyword `chromatography` and the action keyword `purification`. These are primary signals for the `v1` route. The `CBL-B` keyword is a program-class keyword, but chromatography + purification override program keywords in the routing logic. The wiki contains CBL-B program and target science content, but not chromatography column selection guidance. Column selection for a specific protein target is a wet-lab method answer that lives in v1.0.

The session does not attempt to synthesize a column recommendation from wiki content. The correct response is a routing slip directing the query to v1.0.

## Sources

_(none — v1 route bypasses the wiki)_

## Confidence

High on routing decision: `chromatography` + `purification` unambiguously trigger `v1`. The CBL-B program keyword does not override.

## Follow-ups

1. Does v1.0 have a CBL-B-specific purification protocol (e.g., SEC, affinity, IEX column recommendations)?
2. Is there any wiki content in the CBL-B protein sciences pages that mentions column type for CBL-B protein production?

## Filed back?

No. This is a routing slip; no wiki content to file.

## Session notes

Router stress test: CBL-B (program keyword) + chromatography (method keyword) + purification (method keyword). Expected behavior: `chromatography` + `purification` win over `CBL-B`. The benchmark grader should confirm that the system does not retrieve CBL-B wiki pages in response to this query. Compare to q-005 (ÄKTA + BTK) and q-040 (ÄKTA + Pellino-1).
