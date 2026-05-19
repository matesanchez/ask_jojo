---
question_id: q-047
question: "What's the maintenance schedule for the Refeyn mass photometry instrument?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-047
route: wiki
route_decided_by: regex
candidate_slugs:
  - refeyn-mass-photometry
hops_followed:
  - refeyn-mass-photometry
raw_fallback_used: false
raw_entries_read: []
miss_logged: true
confidence: low
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**The wiki does not contain a maintenance schedule for the Refeyn mass photometry instrument. This question cannot be answered from the current wiki corpus.**

The [[refeyn-mass-photometry|REFEYN Mass Photometry]] page (confidence:low) documents the instrument's purpose, measurement principle, Nurix's proof-of-concept demo, sample preparation guidelines, and known troubleshooting observations. It does not contain any maintenance schedule, service interval, or preventive maintenance content. CITED: `refeyn-mass-photometry` — the page does not mention maintenance.

**What the wiki does say about Refeyn status.** The `refeyn-mass-photometry` page states that:
- The REFEYN demo was exploratory; "integration into routine protein QC has not yet occurred."
- "No routine SOPs in place."
- The demo predates routine deployment.

This means the instrument has not reached a stage where a maintenance schedule would typically be documented in the wiki. If a maintenance schedule exists, it would be in an equipment manual, a facilities record, or a v1.0 protocol — not in the wiki as currently populated. CITED: `refeyn-mass-photometry` Status and Recommendations section.

**Miss logged.** This question is logged as a miss because the wiki was queried and found to lack the requested content (maintenance schedule). A raw fallback was not attempted; there is no indication that a raw source for Refeyn maintenance data was ingested.

**Routing note.** The router sent this to `wiki` because `Refeyn` and `mass photometry` are instrumentation keywords with wiki coverage. This routing decision was correct — the wiki does have a Refeyn page. The miss is a content gap, not a routing error. The answer is: the wiki has the instrument, but not the maintenance schedule.

## Sources

- `refeyn-mass-photometry` — primary; instrument description, demo status, no maintenance content. Confidence:low.

## Confidence

Low. The wiki's Refeyn page is confidence:low itself (sourced from a demo-cluster that predates routine deployment). No maintenance schedule was found. The claim "the wiki does not contain a maintenance schedule" is itself high-confidence (a confident absence), but the page's low confidence means even the positive content (instrument description, troubleshooting) is less certain.

## Follow-ups

1. Does the Refeyn instrument's OEM documentation (Cytiva/Refeyn application notes from the demo cluster) contain maintenance schedule information that was not absorbed into the wiki?
2. Has the Refeyn been added to the Nurix equipment inventory with a facilities-managed service schedule post-demo?
3. Would this question be better answered by v1.0 if ÄKTA-adjacent equipment protocols live there, or is it genuinely outside both systems?

## Filed back?

No. There is nothing to file back — the miss confirms a content gap.

## Session notes

Edge case: equipment question where the wiki has a page for the instrument but the page lacks the requested detail. The correct behavior is: route to wiki, retrieve `refeyn-mass-photometry`, find no maintenance schedule, log the miss, and return an honest "not in the wiki" answer. A system that hallucinates a maintenance schedule (e.g., "clean the flow cell weekly, run a calibration bead solution monthly") would fail this benchmark entry immediately. The `refeyn-mass-photometry` page is confidence:low and explicitly says "no routine SOPs in place" — a correctly calibrated system would hedge its output accordingly.
