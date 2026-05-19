---
question_id: q-024
question: "What is the Delphi clone-biomass-protein registration model, and how does a clone move through it?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-024
route: wiki
route_decided_by: regex
candidate_slugs:
  - clone-biomass-protein-registration-model
  - delphi
hops_followed:
  - clone-biomass-protein-registration-model
  - delphi
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: high
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

The Clone-Biomass-Protein Registration Model is the set of metadata fields required when registering a new clone, biomass, or protein lot in [[delphi|Delphi]], Nurix's internal software platform for campaign planning and protein production tracking. It defines what must be recorded at each step in order to prevent IP cross-contamination, support search-and-retrieval queries, and enforce correct financial accounting at registration time [[clone-biomass-protein-registration-model|Clone Biomass Protein Registration Model]].

**Common fields across all three registration types**

The version 2 model (authored by Jose Santos, dated 2020-11-09) defines a single shared field set used identically for clone, biomass, and protein registrations. The six fields are: Project, Program, Contract, Concept, Source, and External Source ID [[clone-biomass-protein-registration-model|Clone Biomass Protein Registration Model]].

- **Project** links the material to a financial accounting category. Materials used across multiple projects use the value "Platform."
- **Program** designates whether the material belongs to a wholly-owned Nurix program or to a collaboration. Allowed values are "Nurix" or "collaboration."
- **Contract** names the external collaborating entity (e.g., "Sanofi," "Gilead") when Program is "collaboration"; it auto-fills to "none" when Program is "Nurix."
- **Concept** records the design origin — who conceived the construct — not who made it. Allowed values are: Nurix Scientist, Published, CRO, Commercial (off-the-shelf only), or Collaborator. When "Published," the same DNA sequence as in the cited publication must be used.
- **Source** records who produced the material. Allowed values are Nurix Scientist (default), CRO (default CRO is Genscript for clones), Commercial (off-the-shelf only), or Collaborator.
- **External Source ID** is the identification number or catalog number from the producing entity; required whenever Source is anything other than Nurix Scientist.

[[clone-biomass-protein-registration-model|Clone Biomass Protein Registration Model]]

**How a gene construct moves through the model**

When a new gene construct enters the pipeline it is first registered as a **clone** in Delphi's Campaign Planning module. The clone record carries all six metadata fields. Clones produced from a Nurix design receive a Nurix clone number in the NBVC-N, NECC-N, or NMAC-N family depending on the expression system. Purchased commercial clones and collaborator-supplied clones also receive a Nurix clone number but carry the external provenance in their metadata fields [[clone-biomass-protein-registration-model|Clone Biomass Protein Registration Model]].

When the clone is taken into fermentation (expression) it generates a **biomass** — a specific expression batch (fermentation lot). If the biomass originates from a Nurix clone, the biomass registration inherits Project, Program, Contract, and Concept automatically from the clone record. If the biomass does not originate from a Nurix clone, all fields must be entered explicitly. Biomasses produced from non-Nurix clones receive the NrxB-N prefix rather than the standard expression nomenclature [[clone-biomass-protein-registration-model|Clone Biomass Protein Registration Model]].

When the biomass is purified to yield a finished lot, the lot is registered as a **protein** in Delphi's Protein Production module. If the protein originates from a Nurix clone or biomass, all metadata fields are inherited. Proteins produced from non-Nurix clones or biomasses require explicit entry and receive an NrxP-N prefix registration number. The NrxP and NrxB prefixes are the explicit signal that the material did not originate from a Nurix clone [[clone-biomass-protein-registration-model|Clone Biomass Protein Registration Model]].

**How protein lots become available for campaign planning**

Once a protein is registered with status "complete" in Protein Production, it becomes available for addition to DEL Screen Plans in Campaign Planning. This is the inter-module contract documented in the Delphi workflow schematics — the protein must clear Protein Production registration before it can be committed to a DEL selection campaign [[delphi|Delphi]].

## Sources

- `clone-biomass-protein-registration-model` — primary page; covers all six metadata fields, the three registration types (clone, biomass, protein), default inheritance rules, and nomenclature distinctions (NrxP, NrxB, NBVC, NECC, NMAC).
- `delphi` — platform page; describes the CP and PP modules and the inter-module protein availability contract.

## Confidence

High confidence: the field definitions, allowed values, and inheritance rules are directly extracted from the `clone-biomass-protein-registration-model` page, which is itself confidence:high with sourced raw files. The Delphi module structure (CP → PP, protein availability trigger) is sourced from `delphi`.

No inferences required; this is a factual description of a documented model.

## Follow-ups

1. What happens in Delphi when a protein registration fails QC — does the lot get a different status, and does that block its appearance in campaign planning?
2. How is the "Concept = Published" rule enforced in practice — is there a validation step that checks the registered sequence against the published sequence?
3. Are NrxP and NrxB registration numbers sequential across all non-Nurix-clone materials, or are they scoped per target or project?

## Filed back?

No. The answer describes the registration model as documented in the existing wiki pages without producing new synthesis.

## Session notes

This question maps cleanly to a single primary page (`clone-biomass-protein-registration-model`) plus the Delphi platform page for context. The three-step arc (clone → biomass → protein) and the inheritance rules are the core of the answer. The version 1 vs. version 2 model distinction (separate field definitions per type vs. unified shared field set) is documented in the wiki but not central to answering the question, so it was not foregrounded.
