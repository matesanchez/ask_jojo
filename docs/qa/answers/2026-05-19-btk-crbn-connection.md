---
question_id: q-036
question: "What is the connection between the BTK program and CRBN/CRL4 at Nurix — is there a molecular glue or PROTAC angle to BTK?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-036
route: wiki
route_decided_by: regex
candidate_slugs:
  - btk-ctm
  - targeted-protein-degradation
  - crbn-cereblon-platform
hops_followed:
  - btk-ctm
  - targeted-protein-degradation
  - crbn-cereblon-platform
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

The BTK program at Nurix is a CRBN-based degrader (PROTAC) program, not a molecular glue program. The [[btk-ctm|BTK CTM Program]] page opens with this explicitly: "The BTK CTM Program at Nurix is a CRBN-based chimeric targeting molecule (CTM) program directed against Bruton's Tyrosine Kinase (BTK), targeting B cell malignancies and autoimmune disease." The CRBN connection is CITED from the wiki.

**Hop 1: BTK CTM uses CRBN as the E3 ligase.** CITED from `btk-ctm`. The program produced three major compounds: NRX-0490492 (NRX-0492), a proof-of-concept tool with BTK IC50 = 1.3 nM and DC50 = 0.37 nM in Ramos cells; NX-2127, a clinical-stage compound that also degrades IKZF1 and IKZF3 in addition to BTK; and NX-5948, the most advanced compound in pharmaceutical development as of 2025-2026.

**Hop 2: What is a CRBN-based CTM?** CITED from `targeted-protein-degradation`. [[targeted-protein-degradation|Targeted Protein Degradation]] explains that PROTACs are bifunctional molecules: a ligand binding the target protein, a linker, and a ligand binding an E3 ligase. The BTK CTMs use the CRBN-binding "harness" (an IMiD-type ligand, consistent with the lenalidomide/pomalidomide series) to recruit BTK to the CRL4-CRBN complex, producing ubiquitylation and proteasomal degradation of BTK. This is the PROTAC modality, not molecular glue.

**Hop 3: CRBN platform context.** The [[crbn-cereblon-platform|CRBN (Cereblon) Platform]] page describes CRBN as "the primary E3 ligase component for thalidomide- and pomalidomide-binding, making it critical for targeted protein degradation (TPD) drug discovery." The page covers DDB1 complex formation, thermal stability studies, CRBN-substrate interaction profiling, and co-expression with regulatory proteins. This platform is shared across multiple Nurix programs, and BTK CTMs draw from it. Confidence on `crbn-cereblon-platform` is **low** (page is flagged as pending source backfill).

**Molecular glue versus PROTAC.** The wiki does not describe any molecular glue angle for the BTK program. Molecular glue degraders stabilize a native protein-protein interaction between the target and a ligase; BTK CTMs are explicitly bifunctional (they carry a separate BTK-binding warhead and a CRBN ligand connected by a linker). The proteomics data in `btk-ctm` shows BTK as the dominant depleted protein, with modest off-target activity at some linker configurations. NX-2127's co-degradation of IKZF1/IKZF3 alongside BTK is a property of the compound, not a reclassification as a molecular glue.

**BTK CTM compound evolution relevant to CRBN.** The program went through four compound generations to optimize the CRBN harness and linker geometry. NRX-0390492 as the oral lead has a Target Candidate Profile requiring CRBN neo-substrate sparing; the program tracked CRBN neo-substrate activity as a selectivity criterion throughout. NX-2127 intentionally retained IKZF1/3 co-degradation as a feature; NX-5948's IKZF selectivity profile is not stated explicitly in the wiki.

## Sources

- `btk-ctm` — primary; CRBN basis of the program, compound evolution, compound series
- `targeted-protein-degradation` — PROTAC mechanism, CRBN in TPD, molecular glue vs PROTAC distinction
- `crbn-cereblon-platform` — CRBN platform context; confidence:low pending source backfill

## Confidence

Highest-confidence: BTK CTM is a CRBN-based PROTAC program (CITED from `btk-ctm`). The three generations of compounds and the CRBN harness design are CITED.

Lower-confidence: The `crbn-cereblon-platform` page is confidence:low, so claims about what Nurix's CRBN platform specifically includes beyond what `btk-ctm` directly states are less certain. The page itself notes that sources are pending backfill from a pre-checkpoint absorb.

No molecular glue angle: no wiki page describes a molecular glue approach to BTK at Nurix; stating "there is no molecular glue angle" is grounded in absence of evidence rather than a positive citation.

## Follow-ups

1. Does NX-5948's pharmaceutical development documentation in the raw corpus clarify its CRBN neo-substrate profile (e.g. sparing of IKZF1/3 versus NX-2127)?
2. The `crbn-cereblon-platform` page is flagged for source backfill — once resolved, will it document the CRBN protein production and DDB1 complex work that supports BTK CTM ternary complex characterization?
3. Are there any Nurix programs that use CRBN in a molecular glue modality (not PROTAC) — would `snf-series-projects` or `gld-series-projects` cover that?

## Filed back?

No. The answer is a synthesis of three existing wiki pages. There is no novel synthesis that rises to a new decision or derived page.

## Session notes

This question is a graph-hop test: BTK program → CRBN → TPD. The hop is clean because `btk-ctm` explicitly names CRBN in its opening sentence, making the connection CITED rather than INFERRED. The molecular glue question is a red herring — molecular glues are not described in any BTK-related wiki page. The router correctly sends this to wiki because `btk` and `crbn` are both program-class keywords with wiki coverage. The `crbn-cereblon-platform` confidence:low flag is the only hedging needed.
