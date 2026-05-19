---
question_id: q-015
question: "What is BTK's role in B-cell receptor signaling, and how does Nurix's BTK CTM program exploit that biology?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-015
route: wiki
route_decided_by: regex
candidate_slugs:
  - btk
  - btk-ctm
hops_followed: []
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**BTK in B-cell Receptor Signaling** [[btk|BTK Target]]

BTK (Bruton's tyrosine kinase) is a non-receptor tyrosine kinase of the TEC family and a central node in B-cell receptor (BCR) signaling. BCR engagement activates BTK, which phosphorylates downstream effectors including PLC-γ2, driving calcium mobilization, NF-κB activation, and ultimately B-cell proliferation, differentiation, and survival. This central role makes BTK a validated target in B-cell malignancies such as CLL, MCL, and Waldenström's macroglobulinemia [[btk|btk]].

Three generations of FDA-approved BTK inhibitors validate the target: covalent inhibitors (ibrutinib), second-generation covalent inhibitors (acalabrutinib, zanubrutinib), and third-generation or non-covalent inhibitors. The major resistance mechanism for the covalent inhibitors is the C481S point mutation at the BTK active site, which eliminates the covalent warhead's thiol-alkylation target while leaving kinase activity intact. Patients on first- and second-generation BTK inhibitors commonly develop C481S resistance [[btk|btk]].

**How the BTK CTM Program Exploits This Biology** [[btk-ctm|BTK CTM Program]]

The Nurix BTK CTM program is a CRBN-based targeted-protein-degradation program that degrades BTK protein rather than occupying its active site. The key biological rationale for degradation over inhibition is C481S resistance: a CTM that recruits BTK to the CRBN-DDB1 E3 ligase complex for ubiquitylation and proteasomal destruction does not rely on covalent modification of Cys481 and therefore retains activity against C481S mutant BTK [[btk-ctm|btk-ctm]]. This is a sub-stoichiometric catalytic mechanism — each CTM molecule can cycle through multiple rounds of degradation, making the approach more efficient than occupancy-based inhibition [[btk-ctm|btk-ctm]].

A proof-of-concept CTM, NRX-0390492, was developed and profiled in HTRF degradation assays in Ramos and TMD8 cell lines [[btk-ctm|btk-ctm]]. The program advanced to clinical candidates:
- NX-2127: degrades both BTK and IKZF1/IKZF3 (a dual-degrader profile). A Science paper was published documenting NX-2127 activity against C481S-resistant BTK [[btk-ctm|btk-ctm]].
- NX-5948: the most advanced compound; in pharmaceutical development as a fumarate salt with SDI/ASD formulation strategy due to poor aqueous solubility; dog PK study completed January 2026 [[btk-ctm|btk-ctm]].

The program targets B-cell malignancies and autoimmune disease [[btk-ctm|btk-ctm]].

## Sources

- `btk` — BTK target page; covers TEC kinase family, BCR signaling role, covalent inhibitor generations, C481S resistance mechanism.
- `btk-ctm` — BTK CTM program page (file: `programs/btk.md`, slug: `btk-ctm`); covers CTM rationale, NRX-0390492 proof-of-concept, NX-2127, NX-5948, NHP pharmacology.

## Confidence

All claims are EXTRACTED from the two cited pages. The BTK target page is rated high confidence. The BTK CTM program page is rated medium confidence. The sub-stoichiometric catalytic description is EXTRACTED from the program page; it is the stated rationale for CTM vs. inhibitor, not an external inference. Confidence: medium overall (limited by program page confidence rating).

## Follow-ups

1. Does the wiki document the C481S activity data for NX-2127 or NX-5948 explicitly (e.g., DC50 in C481S mutant cells vs. wild-type)?
2. The IKZF1/IKZF3 co-degradation by NX-2127 — is this a designed feature or an off-target liability, and is there a wiki entry describing the consequences?
3. Is there a `btk-ind-pharmacology` or `btk-preclinical-profile` page analogous to the CBL-B set?

## Filed back?

No. The answer is a direct synthesis of the target and program pages without novel content.

## Session notes

This question tests the two-layer retrieval needed for target-biology + program questions. The key discriminators are: (a) the three generations of FDA-approved inhibitors are from the target page, not the program page; (b) the C481S mechanistic rationale for CTM is from the program page. Both are required for a complete answer. A system returning only `btk-ctm` would miss the BCR biology; a system returning only `btk` would miss the clinical compounds.
