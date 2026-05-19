---
question_id: q-042
question: "What buffer did we use for the SIAH1 DEL screen?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-042
route: wiki
route_decided_by: regex
candidate_slugs:
  - del-buffer-stability-testing
  - siah1
hops_followed:
  - del-buffer-stability-testing
  - siah1
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**Router decision: `wiki`.** Although the question contains the word `buffer`, this is a DEL screen biochemical-assay buffer question, not a chromatography or ÄKTA buffer question. The correct route is `wiki` because the SIAH1 DEL buffer characterization is documented in the [[del-buffer-stability-testing|DEL Buffer Stability Testing]] method page.

**The SIAH1 buffer composition.** CITED from `del-buffer-stability-testing`.

The buffer stability testing for SIAH1 constructs NBVC-N00619_1A and N00620_1 used a 5X Core Buffer of 20 mM HEPES pH 7.5 with 1 mM MgCl2, diluted into four working buffers that vary on two axes:

- Salt: 150 mM NaCl (low) or 500 mM NaCl (high)
- Detergent: 0.02% detergent (present) or absent

This salt-and-detergent matrix produced four buffer conditions tested against both SIAH1 constructs. Characterization readouts were DSF (thermal stability) and aSEC (oligomeric state and aggregate profile). CITED from `del-buffer-stability-testing` Procedure section.

**Key findings from the buffer testing.** CITED from `del-buffer-stability-testing` Notes section.

- High-salt Buffer 2 (500 mM NaCl) produced aggregates for both NECC-N00619_1A and NECC-N00620_1A.
- Detergent-containing buffers (Buffers 3 and 4) caused loss of the N00620 construct during buffer exchange.
- Lower-salt conditions produced fewer aggregates for N00619.

Next steps documented: test NP40, Tween, and Triton as the detergent; test with and without glycerol; run aSEC under detergent to confirm oligomeric state of exchanged samples.

**The routing distinction.** The `buffer` keyword in this question co-occurs with `DEL screen` and `SIAH1`, which are wiki-class keywords. The question is about biochemical assay buffer (protein stability in a selection campaign), not chromatography buffer. The router should identify this as `wiki` by recognizing the DEL-screen context. A naive regex that routes all `buffer` questions to `v1` would misroute this one.

## Sources

- `del-buffer-stability-testing` — primary; SIAH1 buffer matrix, DSF + aSEC readouts, 5X Core Buffer composition
- `siah1` — SIAH1 target page; construct context (N00619_1A and N00620_1); ALSF collaboration; ELN-252 reference

## Confidence

Highest-confidence: The 5X Core Buffer composition (20 mM HEPES pH 7.5, 1 mM MgCl2) and the four-condition matrix are CITED from `del-buffer-stability-testing`. The results (high-salt aggregation, detergent-caused loss of N00620) are CITED.

Medium-confidence: Whether this pre-screen buffer characterization was the final buffer selected for the live SIAH1 DEL campaign is not stated in the wiki. The buffer-stability testing page covers characterization work, and notes that follow-up axes (NP40, glycerol) were planned. The final campaign buffer may differ. Confidence on "this is the buffer we used in the actual DEL screen" is medium.

## Follow-ups

1. Were the follow-up buffer tests (NP40, Tween, Triton; glycerol) conducted and documented in ELN-252 or a subsequent raw file?
2. What buffer was ultimately selected for the live SIAH1 DEL selection campaign — is that in `2022-del-screen-queue` or a separate campaign file?
3. Does the `del-buffer-stability-testing` page generalize: are there separate buffer characterization pages for other DEL targets (e.g., IRAK4, ZAP-70)?

## Filed back?

No. The answer summarizes existing wiki content without novel synthesis.

## Session notes

This is the edge case mentioned in the benchmark backlog: "'buffer for the SIAH1 DEL screen' — `buffer` keyword; route `wiki` per edge case." The critical design test is that the router does NOT send this to `v1`. A `buffer` + `DEL screen` + program keyword combination should route `wiki` because the DEL screen buffer context is wiki-documented. The benchmark should fail any system that routes this to `v1`. Compare to q-040 (ÄKTA + buffer → v1) and q-041 (chromatography + purification → v1): those have unambiguous equipment/method keywords; this one has only `buffer` plus biochemical-assay context.
