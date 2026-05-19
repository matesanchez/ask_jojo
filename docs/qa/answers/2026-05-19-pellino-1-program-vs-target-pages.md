---
question_id: q-009
question: "What is the difference in scope between the Pellino-1 program page and the Pellino-1 target page — what does each cover that the other doesn't?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-009
route: wiki
route_decided_by: regex
candidate_slugs:
  - pellino-1
  - pellino-1-target
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

The `pellino-1` (program) and `pellino-1-target` pages share the same subject but occupy distinct layers of the wiki: the program page records strategy, decisions, chemistry milestones, and in vivo data; the target page records cell biology, molecular mechanism, and the underlying biological rationale. They do overlap on the Peli2 redundancy question, but they approach it from different angles.

**What the Pellino-1 Program Page covers exclusively** [[pellino-1|Pellino-1 Program]]

- Timeline of the inhibitor phase (2016-2017): FHA domain allosteric binder strategy; micromolar-range potency from early-stage inhibitor work [[pellino-1|pellino-1]].
- CTM phase (2018-2019): transition to CRBN-based degraders as the primary modality.
- Lead CTM NRX-0393000: DC50 = 2.46 nM; first oral CTM compound in the program; MW = 701 [[pellino-1|pellino-1]].
- Pan-Pellino activity of NRX-0393000: Peli2 DC50 = 1.4 nM confirmed by HiBiT screening, making the compound a pan-Pellino degrader rather than a Pellino-1-selective agent [[pellino-1|pellino-1]].
- The 2019 medicinal-chemistry strategic plan comparing Peli1-KO, Peli2-KO, and Peli1+Peli2 double-KO mice in tumor growth inhibition models — the explicit programmatic question of whether to pursue selective Peli1 or pan-Pellino targeting [[pellino-1|pellino-1]].
- In vivo mouse genetics: Peli1-/- mice show TC-1 TGI (p<0.0001 vs WT) and improved MC38 survival; Peli2-/- mice show no TGI in TC-1, no ex vivo T-cell hyperactivation, no slowed MC38 growth [[pellino-1|pellino-1]].
- July 2020 program hurdles: absence of in vitro cellular phenotype from acute CTM treatment; rapid Pellino-1 resynthesis observed in vivo [[pellino-1|pellino-1]].
- Lewis Lanier NK-cell consultation, September 2020 [[pellino-1|pellino-1]].
- Celgene (BMS) collaboration confirmed 2019 [[pellino-1|pellino-1]].
- Medicinal chemistry liability: dioxolane moiety in lead series; NRX-0394704 replacement strategy [[pellino-1|pellino-1]].

**What the Pellino-1 Target Page covers exclusively** [[pellino-1-target|Pellino-1 Target]]

- Molecular biology of PELI1: RING domain E3 ubiquitin ligase; dual roles — negative regulator of T-cell activation (ubiquitinates c-Rel) AND proinflammatory mediator in macrophages (TLR signaling pathway) [[pellino-1-target|pellino-1-target]].
- Jurkat experimental results in full: three independent CRISPR-KO Jurkat lines showing no increase in nuclear c-Rel after CD3/CD28 stimulation; Peli1 siRNA in REAP reporter also showing no effect [[pellino-1-target|pellino-1-target]].
- Weiss lab communication (2017): the specific note that Peli2 expression in Jurkat may compensate for Peli1 loss — this is the cell-biology framing of the redundancy problem [[pellino-1-target|pellino-1-target]].
- Primary T-cell biology: siRNA knockdown showing T-cell hyperactivation (n=8 experiments); CRISPR KO showing IL-2 elevation with divergent TNFα/IFNγ results between sgRNAs [[pellino-1-target|pellino-1-target]].
- THP-1 macrophage assay: shRNA KO reduces LPS-induced cytokines; paradoxical compound-treatment increase in cytokines [[pellino-1-target|pellino-1-target]].
- RIP3 biomarker data: compounds do not upregulate RIP3 in HT-29; CRISPR Peli1 KO in Jurkat does upregulate RIP3 [[pellino-1-target|pellino-1-target]].
- Pellino family member comparison: Peli1 (418aa), Peli2 (420aa, 82% sequence identity), Peli3a/3b (71% identity) [[pellino-1-target|pellino-1-target]].
- Biochemical affinity data: Peli2 shows higher affinity for pIRAK1 pT141 peptide (Kd 0.18 µM) vs Peli1 (0.77 µM) [[pellino-1-target|pellino-1-target]].

**Overlap**

Both pages address the Peli2 redundancy question, but from different angles: the target page frames it as a cell-biological observation (why Jurkat doesn't recapitulate primary T-cell data), while the program page frames it as a strategic question (should the program pursue selective Peli1 or pan-Pellino targeting). A retrieval bundle that returns only one page gives a partial picture of this question.

## Sources

- `pellino-1` — program strategy page.
- `pellino-1-target` — target cell-biology page.

## Confidence

All claims are EXTRACTED from the two cited pages. The overlap characterization is an INFERRED organizational observation derived from reading both pages side by side; the underlying claims are each sourced to one page or the other. Confidence: medium (the overlap characterization is interpretive; the individual facts are high-confidence).

## Follow-ups

1. Is there a `pellino-1-cmc` or `pellino-1-ind-pharmacology` page that would complete the three-layer (target / program / CMC) hierarchy analogous to CBL-B?
2. The July 2020 program hurdles on the program page — is there a corresponding decision document that resolved those hurdles, or did the program end at that point?
3. The Lewis Lanier consultation is cited only by date; is there a separate decisions page or meeting notes document that captures its outcome?

## Filed back?

No. The overlap characterization is a useful synthesis but is too thin (two sentences) to warrant a dedicated page. A note in the program or target page's frontmatter would be a better home for it.

## Session notes

This question tests whether the system treats the program and target pages as distinct entities rather than collapsing them. The two-layer distinction (strategy/decisions vs. biology/mechanism) is a core wiki design principle. A correct answer must cite both pages and correctly assign each piece of content to the right page.
