---
question_id: q-035
question: "What is the HiBiT cell screening assay, and how is it used for target engagement / degradation studies?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-035
route: wiki
route_decided_by: regex
candidate_slugs:
  - cell-screening
hops_followed:
  - cell-screening
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**Principle**

The HiBiT assay (Promega Nano-Glo HiBiT Lytic Detection System) uses a split-NanoLuc bioluminescence system to quantify protein levels in cells. The system has two components: HiBiT, a small 11 amino acid peptide tag genetically fused to the target protein of interest; and LgBiT (Large BiT), a complementary fragment supplied exogenously. HiBiT alone produces minimal background luminescence. When LgBiT is added to cells and associates with the HiBiT tag, the two fragments reconstitute functional NanoLuc luciferase and produce a luminescence signal. The signal is proportional to the amount of HiBiT-tagged target protein present in the cell lysate [[cell-screening|Cell Screening (HiBiT Assay) Methods]].

For degradation studies, when a PROTAC or molecular glue compound drives target protein degradation via the ubiquitin-proteasome system, the amount of HiBiT-tagged target protein decreases, and the luminescence signal falls proportionally. Dose-response experiments measure compound-driven target depletion over time, enabling calculation of degradation potency metrics (e.g., DC50, maximum degradation Dmax) [[cell-screening|Cell Screening (HiBiT Assay) Methods]].

**Nurix implementation**

The HiBiT cell screening assay (V3.0) was established by Isabel Morgado and team. The V3.0 protocol (dated February 14, 2024) incorporates updates from iterative refinement over earlier versions (V2.2, V2.2.1). Isabel's archive contains 704 entries related to cell-screening workflows, spanning method development, protocol refinement, automation integration, and large-scale screening campaigns [[cell-screening|Cell Screening (HiBiT Assay) Methods]].

Compound dispensing uses the Echo acoustic liquid handler (Labcyte) for nanoliter-scale reagent dispensing and sample transfer to multi-well assay plates, improving reproducibility and reducing manual handling. Data upload and analysis are managed through Activity Base LIMS [[cell-screening|Cell Screening (HiBiT Assay) Methods]].

The assay has been deployed at scale: Isabel's archive documents the SNF04 screen series progressing through at least 34 instances (Screen 34 is referenced), representing iterative compound library screening rounds [[cell-screening|Cell Screening (HiBiT Assay) Methods]].

**Quality control**

The V3.0 protocol includes explicit QC criteria for assay acceptance: positive and negative control strategies, signal-to-noise requirements, and curve-fitting parameters for compound potency determination. Isabel documented adherent cell passaging protocols and assay QC criteria [[cell-screening|Cell Screening (HiBiT Assay) Methods]].

**Use in degradation studies**

The assay is directly cited as a readout for PROTAC and molecular glue degrader programs at Nurix. In the CBL-B CTM program, for example, HiBiT cell screening was used to quantify CBL-B protein degradation in response to CRBN-recruiting degraders, with co-degradation of related targets (e.g., Pellino-2 DC50 = 1.4 nM for NRX-0393000) detected by HiBiT screening. The assay therefore functions as the primary cellular degradation readout that connects biochemical compound potency to intracellular target engagement in living cells.

## Sources

- `cell-screening` — primary method page; covers the HiBiT principle, V3.0 protocol implementation, Echo automation, Activity Base LIMS integration, QC criteria, and SNF04 screening scale. Confidence:medium.

## Confidence

Medium confidence. The HiBiT split-NanoLuc principle, V3.0 protocol implementation, Echo automation, and SNF04 scale are sourced from `cell-screening`. The specific mention of "LgBiT" complementation mechanism is sourced from the wiki's description of the assay.

The CBL-B / Pellino-2 DC50 example cited in the "use in degradation studies" section references data documented in the `cbl-b-ctm` wiki page (hops not formally recorded but that page was read during orientation). If strict single-hop sourcing is applied to this answer, the CBL-B example should be understood as INFERRED from adjacent wiki context rather than directly sourced from `cell-screening`. The mechanistic use-case framing is directly sourced from `cell-screening`.

Protocol iterations (V2.2, V2.2.1, V3.0) are noted in the wiki as reflecting ongoing refinement to address earlier issues; the specific problems resolved in each iteration are noted as "partially unabsorbed" in the source page.

## Follow-ups

1. What cell lines are used in the SNF04 screen series for the HiBiT degradation assay — are they stable HiBiT-knockin lines or transient transfection?
2. What is the standard compound incubation time and concentration range in the V3.0 protocol dose-response format?
3. For targets where the HiBiT tag itself affects protein stability or degradation kinetics, does Nurix use an orthogonal degradation readout (e.g., Western blot, mass spectrometry) to confirm the HiBiT result?

## Filed back?

No. The answer describes the existing wiki method page; no novel synthesis is produced.

## Session notes

This is an easy-category question with a single primary page. The HiBiT split-luciferase principle is a well-documented Promega system; the wiki sources it in the context of Isabel Morgado's protocol work. The answer correctly frames HiBiT as a tool for cellular degradation quantification within the PROTAC/molecular glue degrader context, which is Nurix's primary use case. The CBL-B degrader example provides grounding but is noted as drawing from an adjacent page (cbl-b-ctm) not listed in hops_followed — this is flagged transparently in the confidence block.
