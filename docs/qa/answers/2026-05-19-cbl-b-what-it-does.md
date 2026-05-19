---
question_id: q-013
question: "What does CBL-B do biologically, and why is it a therapeutic target for immuno-oncology?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-013
route: wiki
route_decided_by: regex
candidate_slugs:
  - cbl-b-target
  - cbl-b
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

CBL-B is a RING-domain E3 ubiquitin ligase that functions as a negative regulator of immune cell activation, specifically in T cells and NK cells. Its inhibition releases a cell-intrinsic brake on anti-tumor immune responses, making it a rational target for immuno-oncology.

**Molecular Mechanism** [[cbl-b-target|CBL-B Target]]

CBL-B undergoes a conformational switch controlled by phosphorylation at Tyr363 (pY363). In the inactive (closed) conformation, the linker-helix region (LHR) sequesters the RING domain, preventing E2 ubiquitin-conjugating enzyme recruitment. Phosphorylation at pY363 opens this autoinhibited conformation, exposing the RING domain for E2 recruitment and catalytic activity. An inhibitor that stabilizes the closed conformation — or alternatively, occupies the substrate-binding surface — would prevent CBL-B from ubiquitylating its downstream substrates [[cbl-b-target|cbl-b-target]].

**T-Cell Biology**

In T cells, CBL-B ubiquitylates downstream signaling proteins to attenuate TCR signaling. Genetic studies in Cbl-b knockout mice are the foundational in vivo evidence for the therapeutic hypothesis: Cbl-b-/- mice show enhanced anti-tumor activity, and their T cells produce 5-10x more IL-2 and IFNγ compared to wild-type T cells when stimulated [[cbl-b-target|cbl-b-target]]. A ligase-inactive RING mutant (point mutation in the RING domain) was used as a genetic surrogate for pharmacological inhibition, confirming that it is the E3 ligase activity of CBL-B — not scaffolding or adaptor functions — that mediates the immunosuppressive phenotype [[cbl-b-target|cbl-b-target]].

CBL-B also mediates TGF-β sensitivity in T cells via SMAD7 regulation [[cbl-b-target|cbl-b-target]].

**NK Cell Biology**

In NK cells, CBL-B acts downstream of TAM receptors (TYRO3, AXL, and MERTK), which are receptor tyrosine kinases that suppress NK cell activation upon engagement by their phosphatidylserine-exposing ligands (GAS6, PROS1) on tumor cells. CBL-B degrades LAT1, a key adaptor protein in NK cell signaling, thereby suppressing NK cell cytotoxicity [[cbl-b-target|cbl-b-target]]. CBL-B inhibition in this context would be expected to restore NK cell killing of tumor cells that use TAM receptor signaling as an immune evasion mechanism.

**Therapeutic Hypothesis**

The combination of T-cell and NK cell biology makes CBL-B an attractive target for solid tumor immuno-oncology. The Nurix program for CBL-B is a small-molecule E3 ubiquitin ligase inhibitor program, with NX-1607 as the lead clinical compound and NX-0255 developed for ex vivo cell-therapy applications (DeTIL-0255, DeCART) [[cbl-b|cbl-b]]. In syngeneic mouse tumor models (CT-26, MC38, 4T1), CBL-B inhibition showed tumor growth inhibition, with NK cell involvement in the tumor microenvironment as a mechanistic contributor [[cbl-b|cbl-b]].

A notable clarification on clinical signals: NX-1607 does not reduce PSA or proliferation in LnCaP prostate cancer cells in vitro. Clinical PSA reduction observed in mCRPC patients is INFERRED to be immune-mediated rather than a direct tumor-cell effect, based on this in vitro finding [[cbl-b|cbl-b]].

## Sources

- `cbl-b-target` — target biology page; covers pY363 conformational switch, Cbl-b KO mouse data, ligase-inactive RING mutant, TAM receptor NK cell mechanism, TGF-β/SMAD7.
- `cbl-b` — program page; covers syngeneic models, NX-1607 and NX-0255 therapeutic context, PSA clarification.

## Confidence

High-confidence claims: pY363 conformational switch, 5-10x IL-2/IFNγ increase in Cbl-b KO T cells, TAM receptor NK cell mechanism, ligase-inactive RING mutant. These are EXTRACTED directly from the target page. The PSA/clinical claim is marked INFERRED per the wiki. Medium confidence overall because the program page (`cbl-b`) is rated medium confidence.

## Follow-ups

1. Does the target page or any other wiki page describe the specific CBL-B substrate(s) being ubiquitylated in T-cell signaling (e.g., PLC-γ1, PKC-θ, AKT)?
2. Is there a separate wiki page for the DeTIL-0255 or DeCART cell-therapy programs?
3. The Cbl-b KO mouse data (5-10x IL-2/IFNγ) — is this cited to a specific primary publication in the wiki, or is it captured from internal study reports?

## Filed back?

No. The answer synthesizes known wiki content without adding novel analysis.

## Session notes

This is a target-biology question designed to test straightforward retrieval from the target and program pages. A correct answer must hit both the pY363 mechanism (from `cbl-b-target`) and the therapeutic context (from `cbl-b`). Retrieving only one page gives an incomplete answer.
