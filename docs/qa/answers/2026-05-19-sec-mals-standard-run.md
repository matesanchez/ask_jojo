---
question_id: q-031
question: "How does SEC-MALS work, and what does Nurix use it for?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-031
route: wiki
route_decided_by: regex
candidate_slugs:
  - sec-mals
hops_followed:
  - sec-mals
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

SEC-MALS couples two complementary measurement techniques: size-exclusion chromatography (SEC) and multi-angle light scattering (MALS). SEC separates protein species by hydrodynamic radius as they travel through a porous resin — larger species elute earlier, smaller species later. As the separated protein stream exits the column, its concentration is measured by differential refractive index (dRI) detection, and the light scattering signal is recorded simultaneously at multiple angles (typically 15, 90, and 155 degrees). Molecular weight is calculated from the ratio of light-scattering intensity to protein concentration, a calculation that is independent of column calibration standards [[sec-mals|Size-Exclusion Chromatography with Multi-Angle Light Scattering]].

The key advantage over SEC alone is that SEC elution position only estimates size relative to standards of similar shape; MALS provides an absolute molecular weight, unaffected by protein shape, elongation, or glycosylation. For monodisperse proteins (a single oligomeric state), SEC-MALS produces a flat molecular-weight trace across the eluting peak, with a value matching the expected mass from sequence. Aggregates appear as high-mass shoulders; dimers, trimers, and higher oligomers show proportionally increased masses [[sec-mals|Size-Exclusion Chromatography with Multi-Angle Light Scattering]].

**Equipment at Nurix**

Nurix uses Wyatt Technology SEC-MALS systems paired with an AKTA or equivalent liquid chromatography platform. The detector suite includes a dRI detector, a MALS photometer, and optionally a UV detector (280 nm). Column options include Superdex 75 and Superdex 200 resins, covering proteins in the 10 kDa to 600 kDa range. Data processing is performed with Wyatt ASTRA or equivalent software [[sec-mals|Size-Exclusion Chromatography with Multi-Angle Light Scattering]].

**Standard run conditions**

Protein is filtered through a 0.1 micrometer syringe filter immediately before injection to remove aggregates that would distort the light-scattering calculation. Concentration should be in the range of 0.5-5 mg/mL; below 0.5 mg/mL yields weak signals, above 5 mg/mL risks detector saturation. Injection volume is typically 50-100 microliters; flow rate is typically 0.3-0.5 mL/min [[sec-mals|Size-Exclusion Chromatography with Multi-Angle Light Scattering]].

**Use cases at Nurix**

SEC-MALS is used to confirm oligomeric state post-purification, verify complex stoichiometry of multi-subunit assemblies (e.g., E3 ligase dimers or multimeric complexes), and detect aggregation in protein preparations. It is a standard quality control step for recombinant protein characterization and is often required by CROs before protein delivery. Within the broader biophysical characterization progression at Nurix, SEC-MALS occupies the oligomeric-state and aggregation-detection role, complementing DSF (which assesses thermal stability) and intact mass spectrometry (which confirms construct identity) [[sec-mals|Size-Exclusion Chromatography with Multi-Angle Light Scattering]].

**Comparison to alternatives**

SEC-MALS is more accurate than estimating molecular weight from SEC elution time alone (which depends on calibration standards of similar shape). Dynamic light scattering (DLS) measures size and polydispersity but does not separate species and requires more material; SEC-MALS provides both separation and absolute MW accuracy in a single run [[sec-mals|Size-Exclusion Chromatography with Multi-Angle Light Scattering]].

## Sources

- `sec-mals` — primary method page; covers the measurement principle, equipment, sample preparation, data acquisition, applications, troubleshooting, and comparison to alternatives.

## Confidence

Medium confidence. The technical descriptions of the SEC-MALS principle, instrument configuration, run conditions, and use cases are sourced from `sec-mals`. The page itself draws from a cluster of 39 raw OneDrive entries (troubleshooting documentation, instrument maintenance records, LSU training materials, 2020-2026).

No Nurix-specific data (specific protein lots characterized, specific Tm or MW values from SEC-MALS runs) are cited in this answer because none are presented in the `sec-mals` page at the level of individual example experiments.

## Follow-ups

1. What is the Nurix procedure for calibrating the MALS detector — is it done in-house or by Wyatt service visits?
2. For multi-subunit complexes (e.g., CRBN/DDB1 or VHL/Elongin B/Elongin C), has SEC-MALS been used to confirm the stoichiometry of the assembled complex?
3. Are there targets at Nurix where SEC-MALS consistently shows unexpected oligomeric states, requiring construct redesign?

## Filed back?

No. The answer summarizes the existing wiki method page.

## Session notes

This is an easy-category question with a single primary page. The answer correctly distinguishes the SEC separation step (hydrodynamic radius basis) from the MALS weight calculation step (absolute MW, calibration-independent), which is the conceptually important distinction. The use cases (protein QC, complex stoichiometry, CRO delivery requirement) are all sourced from the wiki page.
