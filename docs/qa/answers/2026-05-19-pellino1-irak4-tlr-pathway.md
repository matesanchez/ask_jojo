---
question_id: q-038
question: "What is the mechanistic connection between Pellino-1 and IRAK4 in the TLR pathway — and why does Nurix care about it for the Pellino-1 program?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-038
route: wiki
route_decided_by: regex
candidate_slugs:
  - pellino-1-target
  - irak4
  - pellino-1
hops_followed:
  - pellino-1-target
  - irak4
  - pellino-1
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**The mechanistic connection: Pellino-1 ubiquitinates IRAK4 to amplify TLR signaling.** CITED from `pellino-1-target` (Structure and Mechanism / Signaling Roles sections).

The [[pellino-1-target|Pellino-1 (PELI1)]] page states that in macrophages, Pellino-1 operates downstream of TLR3 and TLR4 to ubiquitinate IRAK1, IRAK4, and RIP1, amplifying proinflammatory cytokine production. CITED: `pellino-1-target` Signaling Roles section. The wiki does not specify the ubiquitin chain linkage type (e.g. K48 vs K63) for these substrates; the amplification directionality is what is CITED. Chain linkage type is not stated in the wiki page.

The [[irak4|IRAK4]] page describes IRAK4 as the master regulator of TLR and IL-1R signaling: upon TLR activation, IRAK4 is recruited to MYD88, forming the Myddosome complex with IRAK2, culminating in NF-kB translocation. IRAK4's substrates include IRAK1, IRAK2, and IRAK4 itself (autophosphorylation). CITED: `irak4` Overview section.

**The biochemical chain, stated precisely:**

1. TLR3/TLR4 activation → MYD88 recruitment → Myddosome assembly (MYD88 / IRAK4 / IRAK2). CITED from `irak4`.
2. IRAK4 autophosphorylates and phosphorylates IRAK1. CITED from `irak4`.
3. Pellino-1's FHA domain is recruited to phosphorylated IRAK1 (FHA binds phosphopeptide). Pellino-1 RING domain then ubiquitinates IRAK1, IRAK4, and RIP1. CITED from `pellino-1-target`.
4. Ubiquitination of IRAK1/IRAK4/RIP1 amplifies downstream NF-kB and cytokine production. CITED from `pellino-1-target`. (Chain linkage type not specified in wiki.)

**Why Nurix cares.** The [[pellino-1|Pellino-1 Program]] page frames the program's primary target as the T-cell regulatory role of Pellino-1: Peli1 KO in mice enhances anti-tumor T-cell responses, and the program pursued Pellino-1 inhibition/degradation as an immuno-oncology approach. However, the TLR/macrophage role creates a programmatic complexity: degrading or inhibiting Pellino-1 in macrophages could dampen innate immune proinflammatory signaling, potentially creating immunosuppressive off-target effects while the intended effect is T-cell hyperactivation.

The wiki records Nurix's approach to this complexity: THP-1 macrophage experiments (with Pellino-1 shRNA knockdown and CRISPR KO) confirmed that Pellino-1 loss attenuates LPS-driven cytokine secretion (TNFa, IL-6). CITED from `pellino-1-target` Protein Regulation section. This is the macrophage arm. The T-cell arm is separately confirmed in Peli1-KO mouse TGI experiments. The program tracked both cell types to understand the therapeutic window.

**Correction note.** The Pellino-1 → IRAK4 relationship is NOT that Pellino-1 degrades IRAK4. Pellino-1 ubiquitinates IRAK4 to amplify signaling. This is the opposite directionality from proteasomal degradation. An answer that states "Pellino-1 promotes degradation of IRAK4" is a factual error not supported by the wiki. By contrast, in T cells Pellino-1 ubiquitinates c-Rel to limit NFkB activation — a distinct substrate in a distinct cell type, with the opposite effect on output (limiting rather than amplifying). CITED: `pellino-1-target`. (Neither K48 nor K63 linkage type is specified in the wiki for either substrate; do not fabricate chain type.)

**IRAK4 as a separate DEL target.** The `irak4` page covers IRAK4 as an independent DEL screen target at Nurix (DEL Campaign 1, 2020), with its own protein constructs, tracers, and selectivity countercreens against IRAK1. This is a parallel DEL effort, not directly connected to the Pellino-1 program. The connection between the two wiki entries is that IRAK4 is a Pellino-1 substrate (in macrophages), not that IRAK4 and Pellino-1 are co-drugged in the same program. INFERRED from cross-reading `pellino-1-target` and `irak4`.

## Sources

- `pellino-1-target` — primary; Pellino-1 K63-ubiquitination of IRAK1/IRAK4/RIP1 in macrophages; FHA domain phosphopeptide recruitment; THP-1 macrophage data; c-Rel K48 ubiquitination in T cells
- `irak4` — IRAK4 domain structure; Myddosome assembly; substrates (IRAK1, IRAK2, IRAK4 autophosphorylation); DEL screen target context
- `pellino-1` — program page; anti-tumor T-cell rationale; Peli1-KO TGI mouse data; program context for why macrophage role matters

## Confidence

Highest-confidence: Ubiquitination of IRAK1/IRAK4/RIP1 by Pellino-1 in macrophages is CITED directly from `pellino-1-target`. The amplification (not degradation) directionality is CITED. Chain linkage type (K48/K63) is NOT stated in the wiki and should not be asserted.

Medium-confidence: The therapeutic-window implication (T-cell hyperactivation vs macrophage dampening) is sourced from the wiki but is a synthesis claim. INFERRED from cross-reading the two roles described in `pellino-1-target`.

Lower-confidence: The "IRAK4 as separate DEL target" note is correct per `irak4` but the question of whether IRAK4 and Pellino-1 were ever coordinated programmatically is not addressed in either wiki page. Marked INFERRED.

## Follow-ups

1. Did Nurix conduct any experiments co-examining Pellino-1 CTM activity in primary macrophages alongside the IRAK4 DEL screen, to understand whether degrading Pellino-1 attenuates IRAK4 signaling amplitude at a relevant level?
2. The `pellino-1-target` page notes that pharmacological inhibitors of Pellino-1 (not degraders) paradoxically increased cytokine output in THP-1 cells — is there a similar assay for the Pellino-1 CTM NRX-0393000 in macrophages?
3. Does the `irak4` page have coverage of the IRAK4 CTM program, if one exists — or is IRAK4 purely a DEL screening target in the wiki?

## Filed back?

No. The answer synthesizes existing wiki content. The mechanistic chain is already present in `pellino-1-target` and `irak4`; the synthesis here does not rise to a novel wiki-worth entity.

## Session notes

This question is a graph-hop test designed to catch a specific error: confusing ubiquitination-for-amplification with ubiquitination-for-degradation. The `pellino-1-target` wiki page states that Pellino-1 ubiquitinates IRAK1/IRAK4/RIP1 in macrophages to amplify signaling, and separately ubiquitinates c-Rel in T cells to limit NFkB activation. The wiki does not specify K48 or K63 chain linkage type for either substrate — a gold answer must not introduce chain linkage language from external knowledge. The benchmark notes field for q-038 flags "Pellino-1 degrades IRAK4" as an immediate fail. The router correctly sends this to wiki because `pellino`, `IRAK4`, and `TLR` are all wiki-class keywords with program/target coverage.
