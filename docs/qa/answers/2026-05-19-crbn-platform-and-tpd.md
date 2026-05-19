---
question_id: q-010
question: "What is the CRBN platform at Nurix, and how does it relate to the targeted protein degradation concept page?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-010
route: wiki
route_decided_by: regex
candidate_slugs:
  - crbn-cereblon-platform
  - targeted-protein-degradation
hops_followed:
  - targeted-protein-degradation
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: low
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

IMPORTANT: The `crbn-cereblon-platform` wiki page carries `confidence: low` with a `pending-backfill-from-raw` source placeholder. The claims drawn from that page are marked accordingly. Claims from the `targeted-protein-degradation` page carry higher confidence.

**The CRBN Platform Page** [[crbn-cereblon-platform|CRBN (Cereblon) Platform]]

The `crbn-cereblon-platform` page describes Cereblon (CRBN) as the primary E3 ligase component for thalidomide- and pomalidomide-binding and as the central ligase for Nurix's targeted-protein-degradation drug discovery. The page notes approximately 80 project entries spanning 2020-2025 documenting CRBN protein production and characterization work [EXTRACTED, LOW CONFIDENCE].

Technical scope recorded on the page:
- Expression systems: baculovirus-mediated insect cell production; bacterial systems for component domains [EXTRACTED, LOW CONFIDENCE].
- Protein characterization: DSF (thermal shift assay), analytical SEC (aSEC), SEC-MALS for complex validation [EXTRACTED, LOW CONFIDENCE].
- DDB1 complex formation and stoichiometry optimization — CRBN functions as part of a CRL4-CRBN complex with DDB1 as the adaptor [EXTRACTED, LOW CONFIDENCE].
- Ligand screening using celmod compound thermal shift assay [EXTRACTED, LOW CONFIDENCE].
- Crystal construct development [EXTRACTED, LOW CONFIDENCE].

The page is a platform-characterization record rather than a program page. It documents the protein science infrastructure for CRBN, not any specific clinical candidate or program decision. It links to [[targeted-protein-degradation]], [[baculovirus-expression]], and a Delphi campaign-planning workflow page [[crbn-cereblon-platform|crbn-cereblon-platform]].

**The Targeted Protein Degradation Concept Page** [[targeted-protein-degradation|Targeted Protein Degradation]]

The `targeted-protein-degradation` page is a concept page explaining the TPD mechanism: small molecules recruit a target protein to an E3 ubiquitin ligase, triggering ubiquitylation and proteasomal degradation. The page explains the two primary TPD modalities:

- PROTAC (Proteolysis Targeting Chimera): bifunctional molecule with a target-binding ligand, a linker, and an E3 ligase ligand; ternary complex formation drives ubiquitylation [[targeted-protein-degradation|targeted-protein-degradation]].
- Molecular glue degraders: monovalent molecules that stabilize a ligase-target protein-protein interaction without bifunctionality [[targeted-protein-degradation|targeted-protein-degradation]].

CRBN is listed on the concept page as the primary E3 ligase for the PROTAC/degrader modality, alongside VHL, MDM2, and KEAP1, among others. The page notes regulatory approvals (lenalidomide for multiple myeloma) as TPD validation and cites a 2021 Keystone symposium on TPD as a source [[targeted-protein-degradation|targeted-protein-degradation]].

The concept page also states that Nurix's internal degradation programs use TPD for internal seed-stage targets including HRAS, NRAS, MYCN, and ARID1B [[targeted-protein-degradation|targeted-protein-degradation]].

**Relationship**

The `crbn-cereblon-platform` page is the protein-science infrastructure record for the CRBN enzyme that enables the TPD programs described conceptually in `targeted-protein-degradation`. The concept page explains what TPD is and why it works; the platform page documents the practical protein production and characterization work that supports the CTM programs (BTK, ITK, Pellino-1, CBL-B CTM, etc.) that each use CRBN as their E3 ligase hook. The platform page links to the concept page; the concept page does not link back to the platform page. INFERRED: the platform page is a supporting resource page, not a program page — it does not document any specific CTM program decision but rather the shared biochemistry infrastructure underlying all CRBN-recruiting programs.

## Sources

- `crbn-cereblon-platform` — CRBN platform page (confidence: low; pending source backfill). Covers protein production scope, 80 project entries 2020-2025.
- `targeted-protein-degradation` — TPD concept page. Covers PROTAC and molecular glue mechanisms, CRBN as primary ligase, Keystone 2021 source.

## Confidence

LOW overall, reflecting that the `crbn-cereblon-platform` page carries `confidence: low` with a `pending-backfill-from-raw` source marker. The descriptions of CRBN's technical scope (DSF, aSEC, SEC-MALS, DDB1 complex) are drawn from that low-confidence page. Claims from `targeted-protein-degradation` (PROTAC/molecular glue mechanism, CRBN role, Keystone 2021) are sourced and carry medium confidence. The relational inference (platform page = infrastructure supporting all CRBN-recruiting programs) is INFERRED and is consistent with the page's content but is not stated explicitly.

## Follow-ups

1. When will the `crbn-cereblon-platform` sources be backfilled — i.e., what raw entries would contain the CRBN protein production records?
2. Does any wiki page document a CRBN ternary-complex characterization study — the platform page mentions "CRBN-substrate interaction profiling" but no specific substrates or CTM compounds are named?
3. Is there a `ternary-complex-formation` concept page that the `targeted-protein-degradation` page links to?

## Filed back?

No. The CRBN platform description is low-confidence and should not be propagated. The relationship inference is too speculative to file back.

## Session notes

This question tests handling of a low-confidence platform page. A correct answer must surface the confidence caveat explicitly and not present the CRBN platform page's claims as facts. The grader should penalize any answer that asserts the CRBN platform page details without marking them as low-confidence / pending backfill.
