---
question_id: q-039
question: "What is SKP2's role in S-phase regulation, and how does that make it a cancer drug target — what was Nurix's approach?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-039
route: wiki
route_decided_by: regex
candidate_slugs:
  - skp2
  - skp2-inhibitor
hops_followed:
  - skp2
  - skp2-inhibitor
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**SKP2's role in S-phase regulation.** CITED from `skp2`.

[[skp2|SKP2 (S-Phase Kinase-Associated Protein 2)]] is an oncogenic F-box protein and the substrate recognition subunit of the SCF-SKP2 E3 ubiquitin ligase complex (SKP1-Cullin1-F-box). Its S-phase role is direct: SKP2 ubiquitylates the CDK inhibitor p27 (CDKN1B), targeting it for proteasomal degradation. By destroying p27, SKP2 removes a brake on CDK2 activity, allowing cells to enter and progress through S phase. CITED from `skp2` Overview.

**Why SKP2 is a cancer target.** CITED from `skp2`.

SKP2 overexpression is observed across many cancers and correlates with poor prognosis. Knockdown of SKP2 inhibits tumor growth in vitro and in vivo. The oncogenic mechanism is the over-destruction of p27 — when SKP2 is overexpressed, p27 is constitutively depleted, CDK2 is hyperactive, and cells progress through S phase inappropriately. CITED from `skp2` Overview.

**The druggable interface: SKP2-Cks1.** CITED from `skp2` Structural Biology and Therapeutic Rationale sections.

The substrate recognition interface between SKP2 and its co-factor Cks1 (CDC28 protein kinase regulatory subunit 1) is the drug target. Efficient p27 ubiquitylation requires Cks1 binding to SKP2; this protein-protein interaction defines a pocket scored as the highest druggability site by computational analysis (ICM Pocket Finder and Schrodinger SiteMap). Crystal structure analysis (Mol Cell, 2005) defined the Skp1-SKP2-Cks1 ternary complex with p27, identifying key contact residues: Arg344, His392, Phe368, Trp265, Asp319 on SKP2; Asn45 and Ser41 on Cks1. Blocking the SKP2-Cks1 interaction was predicted to stabilize p27 and inhibit cell cycle progression. CITED from `skp2`.

**Nurix's approach: three parallel discovery tracks.** CITED from `skp2-inhibitor`.

The [[skp2-inhibitor|SKP2 Inhibitor Program]] ran three hit-finding approaches simultaneously:

1. A biochemical TR-FRET HTS assay measuring competitive displacement of TMR-labeled Cks1 from the Skp1-SKP2 complex (Z-factor = 0.845; Cks1-SKP2 Ki = 1.4 nM). Screening library: ~250,000 compounds from BioFocus lead-like (150,000), Nurix internal (100,000), and WEHI (114,000).
2. Computational virtual screen against the SKP2-Cks1 interface structure.
3. DNA-encoded library (DEL) screen. CITED from `skp2-inhibitor`.

HTS primary screen produced ~2% confirmation rate at TR-FRET + FP dose-response, narrowing to ~0.2% confirmed hits. External collaborators: WEHI (library) and Pharmaron (chemistry support). CITED from `skp2-inhibitor`.

**Program status.** The wiki records the SKP2 program as active approximately 2015–2016. No IND or candidate nomination files are present; the program appears to have concluded without advancing to a development compound. The program predates the CRBN-based CTM platform. CITED from `skp2-inhibitor` Program Status section.

## Sources

- `skp2` — primary; SKP2 biology, p27 ubiquitylation, SCF complex, SKP2-Cks1 interface, therapeutic rationale
- `skp2-inhibitor` — program history; three discovery tracks; HTS performance metrics; program status

## Confidence

Highest-confidence: SKP2 → p27 ubiquitylation → S-phase entry chain is CITED directly from `skp2`. The three discovery tracks are CITED from `skp2-inhibitor`.

Medium-confidence: Program status ("concluded without advancing to development compound") is stated in `skp2-inhibitor` but hedged with "appears to have concluded" — the wiki does not have an explicit decision page recording program termination. Confidence is medium for the program status claim.

No claims about current SKP2 biology in the broader field beyond what the wiki states.

## Follow-ups

1. Did the DEL screen for SKP2 yield hits, and if so, are they documented in `del-screening` or a separate SKP2 DEL results page?
2. Was a SKP2 CTM (PROTAC/degrader) ever considered after the CRBN platform was established (post-2016)? No CTM page for SKP2 exists in the wiki.
3. Does the WEHI collaboration on the SKP2 program have any documented outcomes (publications, compound transfers)?

## Filed back?

No. The answer summarizes two existing wiki pages without producing novel synthesis.

## Session notes

This is a target-biology + program-history question testing two-hop retrieval: the biology is on `skp2` (target page) and the program history is on `skp2-inhibitor` (program page). A retrieval system that returns only one will produce a partial answer. The key conceptual point — SKP2 does NOT directly regulate S-phase, it does so indirectly by destroying the CDK2 brake p27 — is what the benchmark should grade. A correct answer names both SKP2 and p27 and explains the ubiquitin-mediated mechanism. An answer that says "SKP2 is a kinase involved in S-phase" is wrong (SKP2 is an F-box protein, not a kinase) and should be flagged as a fail.
