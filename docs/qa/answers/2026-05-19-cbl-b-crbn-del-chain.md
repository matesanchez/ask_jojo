---
question_id: q-037
question: "Trace the chain from the CBL-B program to the CRBN platform to the DEL screening platform — how are they connected?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-037
route: wiki
route_decided_by: regex
candidate_slugs:
  - cbl-b
  - cbl-b-ctm
  - crbn-cereblon-platform
  - targeted-protein-degradation
  - del-screening
  - del-libraries
hops_followed:
  - cbl-b
  - cbl-b-ctm
  - crbn-cereblon-platform
  - targeted-protein-degradation
  - del-screening
  - del-libraries
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

The CBL-B → CRBN → DEL chain is a three-node graph in the Nurix wiki, and the links between each node are explicitly stated (CITED) rather than inferred.

**Node 1: CBL-B program ([[cbl-b|CBL-B Program]]).** The CBL-B inhibitor program (NX-1607 lead) traces its origin to a 2015 DEL screen run through Vipergen. The `cbl-b` page lists `del-screening` as a related page and establishes that the inhibitor chemotype was discovered via DNA-encoded library selection. CITED: the overview notes the Vipergen 2015 screen as the origin of the inhibitor series.

**Node 2: DEL connection to CBL-B CTM ([[cbl-b-ctm|CBL-B CTM Program]]).** The CBL-B CTM (PROTAC/degrader) program's starting material — NRX-0395370, the parental inhibitor used to build the CRBN-conjugated tool molecules — is "a DEL series 1 hit from the same Vipergen screen that yielded the inhibitor series." CITED: `cbl-b-ctm` Overview section. This is the direct link between DEL screening and the CRBN-based arm of the CBL-B effort. The carboxylic acid at the DNA attachment point of the DEL molecule pointed toward solvent in the co-crystal structure and was used as the exit vector for CTM linker attachment — meaning the DEL chemistry directly enabled the CRBN conjugation design.

**Node 3: CBL-B CTM uses CRBN ([[crbn-cereblon-platform|CRBN Platform]]).** The `cbl-b-ctm` page is tagged `crbn` and lists `crbn-cereblon-platform` as a related page. The page describes that the first confirmed CRBN-based CTM in the series, NRX-0395686, was confirmed CRBN-mediated by NAE1-inhibitor rescue assay, with DC50 ~250 nM (Ramos cells). CITED: `cbl-b-ctm`. The CRBN harness draws from the broader [[targeted-protein-degradation|Targeted Protein Degradation]] platform; `targeted-protein-degradation` lists CRBN as the classical E3 for thalidomide-family PROTAC programs.

**The complete chain, stated concisely:**

1. DEL screen (Vipergen 2015) → identified NRX-0395370 as a CBL-B binder. CITED from `cbl-b-ctm`.
2. NRX-0395370 DEL hit → used as the target-binding warhead in the CRBN CTM series. CITED from `cbl-b-ctm`.
3. CRBN harness conjugated to NRX-0395370 scaffold → produced CBL-B degraders including NRX-0395686. CITED from `cbl-b-ctm`.
4. CRBN platform → shared infrastructure for thalidomide-family E3 ligase recruitment across Nurix TPD programs. CITED from `crbn-cereblon-platform` (confidence:low) and `targeted-protein-degradation`.

**Platform vs program relationship.** The [[del-screening|DEL Screening Program]] page and [[del-libraries|DEL Libraries]] page describe the broader DEL infrastructure at Nurix (libraries D1–D5, NRX09, NRX04 Covalent, etc.) used across programs. The Vipergen screen is one instance of this DEL capability applied to CBL-B. The DEL output fed both the inhibitor program (NX-1607 chemotype) and, via the same hit NRX-0395370, the degrader/CTM program. The CRBN platform (`crbn-cereblon-platform`, confidence:low) then provided the E3-ligase machinery for the degrader arm. The chain is therefore: DEL Platform → CBL-B hit → CBL-B Inhibitor Program (NX-1607) AND CBL-B CTM Program (CRBN-based) → CRBN Platform.

**One caveat.** The `crbn-cereblon-platform` page carries confidence:low and is flagged for pending source backfill. Claims about the CRBN platform beyond what `cbl-b-ctm` directly states are less certain. The chain's first three links are fully CITED from `cbl-b-ctm`; the fourth link (CRBN platform generality) is grounded in `targeted-protein-degradation` (confidence:medium) as a backstop.

## Sources

- `cbl-b` — CBL-B inhibitor program; DEL origin of NX-1607 chemotype; relation to `del-screening`
- `cbl-b-ctm` — primary; NRX-0395370 as DEL hit and parental compound; CRBN-based CTM series; NRX-0395686 DC50
- `crbn-cereblon-platform` — CRBN platform context; confidence:low, sources pending backfill
- `targeted-protein-degradation` — PROTAC mechanism; CRBN as classical E3 in TPD
- `del-screening` — DEL screening program structure; Vipergen screen context
- `del-libraries` — DEL library portfolio; NRX09 default library 2022

## Confidence

Highest-confidence: The NRX-0395370 DEL hit → CRBN CTM connection is directly and explicitly stated in `cbl-b-ctm`. This is the load-bearing link in the chain.

Medium-confidence: The broader DEL platform → CBL-B connection is stated in `cbl-b` with `del-screening` as a related page, but the `cbl-b` page itself is confidence:medium.

Lower-confidence: `crbn-cereblon-platform` is confidence:low; the CRBN platform's full scope beyond what `cbl-b-ctm` states draws from `targeted-protein-degradation` as a backstop.

## Follow-ups

1. Does `del-screening` explicitly name the Vipergen 2015 screen as the source of the CBL-B hit, or is that attribution only in `cbl-b-ctm`?
2. Did the CBL-B CTM program explore E3 ligases other than CRBN beyond the 2017-2018 VHL exploratory phase? If so, are those on the CRBN platform page or the CBL-B CTM page?
3. Once `crbn-cereblon-platform` is backfilled with sources, will it document the DDB1 co-expression work that underlies the CBL-B CTM ternary complex?

## Filed back?

No. This is a synthesis of existing wiki content. The chain is already implicit in the related-pages links; making it explicit in a new wiki page would add value only after `crbn-cereblon-platform` is fully sourced.

## Session notes

This is a 3-hop relational question stress-testing graph traversal. The key insight is that the same DEL hit (NRX-0395370) spawned both the inhibitor program and the degrader program — a bifurcation that's easy to miss if the retrieval returns only `cbl-b` and misses `cbl-b-ctm`. The benchmark retrieval test should require both pages to be surfaced. The `crbn-cereblon-platform` confidence:low flag propagates into the answer's confidence for the platform node; the router correctly sends this to wiki since `cbl-b`, `crbn`, and `del` are all wiki-class keywords.
