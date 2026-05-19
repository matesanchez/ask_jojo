---
question_id: q-045
question: "What are the most common errors in the UNICORN method editor when setting up a new gradient?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-045
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

The question contains the ÄKTA software keyword `UNICORN` and the method keyword `gradient`, both of which are primary v1-routing triggers. UNICORN is the GE/Cytiva software used to control ÄKTA chromatography systems; questions about its method editor are pure instrument-software questions with no wiki coverage. The wiki has no UNICORN or gradient method content. There are no program-class keywords in this question.

The session does not attempt to answer this question from the wiki. The correct response is a routing slip directing the query to v1.0.

## Sources

_(none — v1 route bypasses the wiki)_

## Confidence

High on routing decision: `UNICORN` + `method editor` + `gradient` are unambiguous v1 signals. No competing wiki keywords present.

## Follow-ups

1. Does v1.0 have a troubleshooting guide for UNICORN method editor errors (e.g., gradient validation failures, pressure limit overrides)?
2. Is there a Nurix-specific UNICORN method template library in v1.0?

## Filed back?

No. This is a routing slip; no wiki content to file.

## Session notes

Pure v1-routing test: UNICORN + method editor + gradient, no program context. This is the backlog stub: "'UNICORN method-editor common errors' — pure v1 question." Should be an unambiguous v1 route with no hesitation. The benchmark should confirm that the system does not attempt to retrieve wiki content.
