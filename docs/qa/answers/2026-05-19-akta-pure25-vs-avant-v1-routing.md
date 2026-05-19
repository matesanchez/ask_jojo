---
question_id: q-044
question: "What's the difference between the ÄKTA Pure 25 and the ÄKTA Avant — which one should I use for protein purification?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-044
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

The question contains explicit ÄKTA instrument names (`ÄKTA Pure 25`, `ÄKTA Avant`) and the method keyword `protein purification`. All three signals are primary v1-routing triggers. The wiki has no content for ÄKTA instruments (`equipment/akta/` directory is empty per `_index.md`); instrument comparison and selection guidance live in v1.0. There are no program-class keywords in this question that could create routing ambiguity.

The session does not attempt to answer this question from the wiki. The correct response is a routing slip directing the query to v1.0.

## Sources

_(none — v1 route bypasses the wiki)_

## Confidence

High on routing decision: `ÄKTA Pure 25` + `ÄKTA Avant` + `purification` are unambiguous v1 signals. No competing wiki keywords present.

## Follow-ups

1. Does v1.0 include a comparison page for ÄKTA Pure 25 vs ÄKTA Avant (flow rate range, column capacity, fraction collector options)?
2. Is there a Nurix instrument selection SOP in v1.0 that maps protein size/volume to instrument choice?

## Filed back?

No. This is a routing slip; no wiki content to file.

## Session notes

Pure v1-routing test: both ÄKTA instrument names are mentioned with no program context. This should be the cleanest possible v1 route — no competing signals. The benchmark should confirm that the router never hesitates on this one. Compare to q-005 (ÄKTA + program keyword + buffer): this version is simpler because there is no program keyword to compete.
