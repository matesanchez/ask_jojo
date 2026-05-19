---
question_id: q-023
question: "What is the CRBN molecular glue mechanism, and how does it differ from a PROTAC?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-023
route: wiki
route_decided_by: regex
candidate_slugs:
  - crbn-cereblon-platform
  - targeted-protein-degradation
hops_followed:
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

**Mechanistic distinction: molecular glue vs. PROTAC**

Both molecular glues and PROTACs exploit the ubiquitin-proteasome system to destroy a target protein, but they achieve E3 ligase recruitment through fundamentally different structural strategies [[targeted-protein-degradation|Targeted Protein Degradation]].

A PROTAC is a bifunctional molecule with three distinct domains: a ligand for the target protein, a chemical linker, and a ligand for an E3 ligase. The linker acts as a bridge, physically connecting the two binding events and forcing the target into proximity with the ligase. Productive ternary complex formation — the simultaneous binding of target, PROTAC, and ligase — leads to target ubiquitylation and degradation. PROTAC discovery therefore requires optimizing both binding moieties and the linker geometry to achieve this three-body assembly [[targeted-protein-degradation|Targeted Protein Degradation]].

A molecular glue degrader is typically a small, monofunctional compound. Rather than connecting two pre-existing binding sites with a linker, a molecular glue stabilizes a protein-protein interaction between the target protein (the neosubstrate) and the E3 ligase that would not form — or would form only weakly — in the molecule's absence. The compound acts as a "glue" that creates a composite binding surface recognized jointly by both proteins. Because there is no bifunctional linker, molecular glues tend to be smaller and more drug-like by Lipinski criteria, and may achieve higher selectivity because they exploit an existing ligase-substrate recognition pathway rather than creating a fully synthetic bridge [[targeted-protein-degradation|Targeted Protein Degradation]].

Cereblon (CRBN), the primary E3 ligase component of the CRL4-CRBN E3 ligase complex, is the target of the immunomodulatory drugs (IMiDs) thalidomide and lenalidomide. These compounds and their structural derivatives function as molecular glues: they bind CRBN and create a new surface that recruits neosubstrates (e.g., Ikaros, Aiolos, GSPT1) for ubiquitylation and degradation. The molecular basis is induced complementarity — the drug changes CRBN's surface topology to match the substrate, rather than acting as a linker between two independent binders [[targeted-protein-degradation|Targeted Protein Degradation]].

**Nurix's CRBN platform work**

The `crbn-cereblon-platform` wiki page documents Nurix protein sciences work on the CRBN/DDB1 complex, including expression, complex assembly, and thermal stability characterization with Celmod (cereblon modulator) compounds [[crbn-cereblon-platform|CRBN Cereblon Platform]]. Expression systems documented include baculovirus-mediated insect cell production and bacterial systems for component domains. Characterization methods include DSF, analytical SEC (aSEC), and SEC-MALS for complex validation [[crbn-cereblon-platform|CRBN Cereblon Platform]].

INFERRED: the Celmod compound binding data documented in the CRBN platform work is consistent with Nurix investigating molecular glue-type CRBN modulators (compounds that bind CRBN and modulate neosubstrate recruitment), given the known biology of Celmod compounds. However, the `crbn-cereblon-platform` wiki page does not explicitly name specific molecular glue compounds or clinical candidates, and its sources are marked as pending backfill. Any claim about specific Nurix molecular glue series must await source resolution.

## Sources

- `targeted-protein-degradation` — primary mechanistic page; covers PROTAC and molecular glue mechanisms, CRBN as an E3 ligase, and the induced-complementarity model for molecular glues.
- `crbn-cereblon-platform` — Nurix CRBN platform page; covers CRBN/DDB1 complex characterization and Celmod compound thermal stability data. **Note: this page carries `confidence: low` with sources marked as pending-backfill-from-raw. Claims specific to Nurix's CRBN compound series are hedged accordingly.**

## Confidence

High confidence: the mechanistic distinction between PROTAC (bifunctional linker) and molecular glue (induced complementarity, monofunctional) is sourced from `targeted-protein-degradation`, which is confidence:medium with a clear source.

Lower confidence — explicitly flagged: the `crbn-cereblon-platform` page is confidence:low with pending source backfill. Nurix-specific details about the CRBN platform (expression systems, characterization methods, Celmod compound work) are drawn from that page and should be understood as provisionally accurate until the source backfill is completed. No named molecular glue compounds or clinical candidates from Nurix's CRBN program are cited because none appear in the sourced wiki content.

## Follow-ups

1. Which neosubstrates has Nurix profiled for CRBN-mediated degradation in the Celmod compound series?
2. Has Nurix characterized the structural basis for any CRBN-molecular glue ternary complex using crystallography or cryo-EM?
3. What is the current status of the `crbn-cereblon-platform` wiki page source backfill — are the original raw entries accessible?

## Filed back?

No. The mechanistic content is already in `targeted-protein-degradation`; the Nurix-specific CRBN details are bounded by the low-confidence source status of `crbn-cereblon-platform`.

## Session notes

The key discipline issue here is the confidence:low status of `crbn-cereblon-platform`. The mechanistic explanation (glue vs. PROTAC) is soundly sourced in `targeted-protein-degradation`. The Nurix application details are hedged because the CRBN platform page is not yet fully sourced. The INFERRED label on the Celmod-as-molecular-glue claim is correct given the gap between what the wiki says explicitly vs. what is inferable from domain knowledge about Celmod compound classes.
