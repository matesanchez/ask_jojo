---
question_id: q-040
question: "What's the standard buffer prep procedure for an ÄKTA run on the Pellino-1 protein?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-040
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

The question contains the equipment keyword `ÄKTA` and the method keyword `buffer prep`. These are the primary signals for the `v1` route. The `Pellino-1 protein` phrase is a program-class keyword that might otherwise suggest the `wiki` route, but ÄKTA + buffer is a v1 signal that overrides program keywords. The wiki has no ÄKTA equipment content (`equipment/akta/` directory is empty per `_index.md`); the answer — a chromatography buffer preparation procedure — lives in the v1.0 system.

The session does not attempt to answer this question from the wiki. The correct response is a routing slip directing the query to v1.0.

**What a correct v1.0 answer would cover** (for benchmark graders only, not synthesized from wiki): standard ÄKTA buffer prep procedures, including buffer degassing, pH verification, filter prep, and any Pellino-1-specific buffer conditions that may be documented in v1.0 ÄKTA methods. This system does not attempt to specify those details.

## Sources

_(none — v1 route bypasses the wiki)_

## Confidence

High on routing decision: ÄKTA + buffer keywords unambiguously trigger `v1`. The Pellino-1 program keyword does not override.

## Follow-ups

1. Does v1.0 have a Pellino-1-specific ÄKTA purification protocol, or only generic buffer prep guidance?
2. Is there any wiki content (e.g., under `pellino-1` program page) that documents the Pellino-1 purification buffer composition from protein sciences?

## Filed back?

No. This is a routing slip; no wiki content to file.

## Session notes

Router stress test: Pellino-1 (program keyword) + ÄKTA (equipment keyword) + buffer (method keyword). The expected behavior is that `ÄKTA` + `buffer` win over `Pellino-1`. This mirrors the BTK ÄKTA buffer test (q-005). The benchmark should confirm that the regex does not over-rotate to `wiki` because of the program name. Compare to q-005 (BTK ÄKTA buffer) — same structure, different program name.
