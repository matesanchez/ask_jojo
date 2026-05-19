---
question_id: q-032
question: "How does DSF work, and what is it used for in protein characterization at Nurix?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-032
route: wiki
route_decided_by: regex
candidate_slugs:
  - dsf
hops_followed:
  - dsf
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

Differential scanning fluorimetry (DSF) measures protein thermal stability by monitoring fluorescence changes as a protein solution is heated through its melting transition. The assay uses an extrinsic fluorescent dye — typically SYPRO Orange — that shows low fluorescence in aqueous solution but fluoresces strongly when it binds to hydrophobic protein surfaces exposed during denaturation. As the protein unfolds, increasing amounts of hydrophobic surface become accessible, driving a rise in fluorescence signal. The melting temperature (Tm) is derived from the peak of the first derivative of fluorescence versus temperature. A higher Tm indicates a more thermally stable protein; ligand binding that stabilizes the folded state shifts Tm to higher values (positive delta-Tm) [[dsf|Differential Scanning Fluorimetry (DSF)]].

The Niesen et al. (Nature Protocols 2007) paper is the foundational DSF protocol reference; Hall et al. (Protein Science 2019) describes extracting binding affinity estimates from thermal shift data under specific conditions [[dsf|Differential Scanning Fluorimetry (DSF)]].

**Technical implementation at Nurix**

Isabel Morgado's work at Nurix employed the Tycho instrument (NanoTemper) for DSF measurements. The Tycho is a capillary-based system suitable for small sample volumes (2-10 microliters); measurements take approximately 15-20 minutes per sample. DSF can be run on real-time PCR instruments as well (with SYPRO Orange and a standard qPCR machine), making it compatible with high-throughput plate formats [[dsf|Differential Scanning Fluorimetry (DSF)]].

**Use cases at Nurix**

DSF is used for four principal applications in Nurix protein characterization [[dsf|Differential Scanning Fluorimetry (DSF)]]:

1. **Post-purification protein quality assessment.** After a protein production run, DSF confirms that the purified construct has a defined melting transition, indicating it is folded. A poorly folded or heterogeneous preparation may show a broad or absent transition.

2. **Buffer optimization.** DSF screens buffer components (salt concentration, pH, detergent presence, glycerol, additives) to identify conditions that maximize Tm and therefore protein stability. Isabel Morgado documented buffer-optimization studies across multiple constructs and protein targets using this approach.

3. **Ligand binding and hit identification.** Ligand binding that stabilizes the folded state produces a positive delta-Tm. DSF is therefore used to confirm that a DEL hit or resynthesized compound genuinely binds to the target. DSF was applied to ternary complex assessment (e.g., AuroraA-NMYC-CRBN-DDB1 complex, where compounds NRX4505 and NRX6715 showed thermal shifts in the complex).

4. **Protein stability comparison across constructs.** When multiple expression constructs are evaluated (e.g., different domain boundaries, mutation variants), DSF provides a rapid rank-order of thermal stability to guide construct selection.

**Limitations**

Common pitfalls include protein precipitation during heating (which reduces signal), pH-dependent Tm variation (buffer pH must be controlled), and interference from assay components (DMSO, glycerol) that shift Tm. DMSO concentration in compound binding assays should be controlled with matched vehicle blanks. DSF provides thermodynamic stabilization information only, not binding kinetics or mechanism [[dsf|Differential Scanning Fluorimetry (DSF)]].

DSF is faster and requires far less material than differential scanning calorimetry (DSC) but provides less thermodynamic detail. It is typically used for medium-throughput screening and prioritization before investing in kinetic characterization by SPR or ITC [[dsf|Differential Scanning Fluorimetry (DSF)]].

## Sources

- `dsf` — primary method page; covers the principle, Tycho instrument implementation, buffer optimization applications, ligand binding use case, and common pitfalls.

## Confidence

Medium confidence. The DSF principle (SYPRO Orange dye, Tm from derivative, delta-Tm for ligand binding) and the Nurix applications (buffer optimization, hit confirmation, complex characterization) are sourced from the `dsf` wiki page, which draws from Isabel Morgado's DSF archive (11 entries) and the Niesen 2007 and Hall 2019 references.

The specific compound examples (NRX4505, NRX6715, AuroraA-NMYC-CRBN-DDB1) are cited from the `dsf` page and should be understood as illustrative examples from Isabel's archive rather than exhaustive program data.

## Follow-ups

1. What delta-Tm threshold does Nurix use to call a compound a "confirmed binder" in DSF, and is it consistent across target classes?
2. For which targets has DSF been used to drive buffer selection that subsequently fed into DEL screen campaigns?
3. How does Nurix reconcile a positive DSF shift with a negative binding result in an orthogonal assay (e.g., SPR shows no binding despite positive delta-Tm)?

## Filed back?

No. The answer describes the existing wiki method page without novel synthesis.

## Session notes

DSF is used broadly across protein sciences workflows at Nurix, appearing in the buffer stability testing SOP (q-030), the protein QC report requirements (q-029 protein request protocol), and the ternary complex assay context. The answer correctly positions DSF in the medium-throughput/preliminary-screening role and flags the limitations around kinetics and thermodynamics. The Tycho instrument is the primary implementation tool cited in the wiki.
