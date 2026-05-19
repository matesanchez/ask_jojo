---
question_id: q-002
question: "Did the Weiss lab Peli2 redundancy finding in Jurkat ever change our position on the Pellino-1 program direction?"
asked_by: mateo
asked_date: 2026-04-30
session_date: 2026-04-30
session_id: cowork-2026-04-30-002
route: wiki
route_decided_by: regex
candidate_slugs:
  - pellino-1
  - pellino-1-target
hops_followed:
  - targeted-protein-degradation
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

The Weiss laboratory's Peli2-redundancy observation in Jurkat is a documented but bounded finding in the [[pellino-1|Pellino-1 Program]] record, and the wiki's reading of its program-direction impact is "informed but did not change" rather than "redirected." The finding itself is a 2017 communication from the Weiss lab noting that Peli1 alone failed to produce activity in their RE/AP reporter screen in Jurkat, and that Peli2 expression in Jurkat may compensate for Peli1 loss [[pellino-1-target|pellino-1 (target)]]. Nurix internal CRISPR Peli1-knockout Jurkat lines reproduced the Weiss negative — three independent lines showed no increase in nuclear c-Rel after CD3/CD28 stimulation, and Peli1 siRNA in the REAP reporter assay also produced no effect [[pellino-1-target|pellino-1 (target)]]. Functional redundancy between Peli1 and Peli2 in this cell line is the wiki's stated explanation for the absence of phenotype, consistent with the known limitation of Jurkat as a T-cell model.

The program response to the Jurkat-redundancy observation was to evaluate dual Peli1/Peli2 targeting rather than abandon the program. The 2019 medicinal-chemistry plan for the Pellino-1 program included a comparison of Peli1-knockout, Peli2-knockout, and Peli1+Peli2 double-knockout mice in tumor growth inhibition models, with the explicit goal of deciding whether selective Peli1 or pan-Pellino targeting was the right approach [[pellino-1|pellino-1]]. The eventual answer in mice was that Peli1, not Peli2, drives the anti-tumor immune phenotype: Peli2-/- mice did not show TGI in the TC-1 model and did not show ex vivo T-cell hyperactivation, and there was also no slowed tumor growth in the MC38 model for Peli2-/- mice [[pellino-1|pellino-1]]. This is in contrast to the Jurkat result; the wiki frames the discrepancy as a Jurkat-specific limitation rather than a redirection of program direction.

The lead Pellino-1 CTM compound NRX-0393000 was subsequently confirmed to be a pan-Pellino degrader after Peli2 HiBiT screening showed co-degradation of Pellino-2 with DC50 = 1.4 nM [[pellino-1|pellino-1]]. The wiki notes this as "making the compound a pan-Pellino degrader" without recasting the program's stated target, which remains Pellino-1. The pan-degradation is therefore a *property* of the lead, observed and recorded, rather than a *strategic* decision to switch to a pan-Pellino target. INFERRED: the program direction did not change in response to the Weiss/Jurkat finding; it was confirmed by primary mouse-genetic data, and the lead compound's pan-Pellino activity emerged as a chemical property the program tracked rather than a redirection.

## Sources

- `pellino-1` (program) — primary program-level page; covers the 2019 medchem plan and the Peli1 vs Peli2 vs double-KO mouse comparison. Lewis Lanier consultation in September 2020 also captured here.
- `pellino-1-target` — target biology page; carries the full Weiss-lab communication and the Nurix Jurkat CRISPR-KO replication. Also covers the THP-1 macrophage studies and the RIP3 biomarker findings.
- `targeted-protein-degradation` — read once for context (the program is a CTM/degrader program); not directly cited in the answer.

## Confidence

Highest-confidence claims: (a) the Weiss lab finding is documented in the wiki and was reproduced by Nurix CRISPR-KO Jurkat lines; (b) the Peli2-/- mouse TGI data did not show a phenotype in TC-1 or MC38, supporting Pellino-1 as the primary target.

Lowest-confidence claim: "the program direction did not change in response to the Weiss/Jurkat finding." Marked INFERRED. The wiki does not contain an explicit decision page on this question — there is no `decisions/pellino-1-direction-2017.md` or similar artifact. The inference is drawn from the absence of a redirection (the 2019 medchem plan still names Pellino-1, the lead compound is named for Pellino-1 even after pan-degradation is confirmed) rather than from a positive statement that the team chose to stay the course. A future absorb pass that surfaces the early-2018 program decision artifact would either confirm or refine this. Confidence is set to `medium` for the answer overall to reflect this gap.

The two cited pages are internally consistent. The target page is more biology-detailed; the program page is more strategy-oriented. They reinforce each other on the Peli1 vs Peli2 question and do not disagree.

## Follow-ups

1. Is there a 2017–2018 program decision document captured in raw that explicitly weighs the Jurkat-redundancy finding against the mouse genetics, or did the team treat the mouse data as authoritative?
2. What downstream consequences did the pan-Pellino degradation property of NRX-0393000 have for clinical-candidate selection — i.e. did selectivity vs Pellino-2 ever become a go/no-go criterion?
3. Did the Lewis Lanier NK-cell consultation (September 2020) propose any experiments specifically aimed at distinguishing Peli1-only from pan-Pellino activity?

## Filed back?

No. The answer summarizes existing wiki content without producing novel synthesis worth promoting. The "INFERRED: program direction did not change" framing is borderline (it is a synthesis claim drawn from absence of evidence, not from a primary source), but its uncertainty is the reason not to file it back as a wiki page — it would propagate a low-confidence inference into the wiki's "fact" surface.

## Session notes

This question stress-tested the EXTRACTED-vs-INFERRED discipline. The most natural answer ("yes, the Weiss finding caused us to re-evaluate") is unsourced and would have been a hallucination; the actual evidence in the wiki supports a more bounded answer ("the finding informed the dual-KO experimental plan, the mouse data resolved it, and the program continued with Pellino-1 as the named target"). Worth recording as a benchmark question for future regression testing.

One prompt-tightening note: the wiki's program page and target page have overlapping but non-identical Peli2-redundancy coverage. The program page emphasizes the strategic question (selective vs pan-Pellino targeting) and the program page emphasizes the cell-biology question (why Jurkat doesn't recapitulate). A retrieval bundle that returns *both* is necessary; returning either alone would have produced a partial answer. The retrieval logic in `packages/jojo_qa/index_loader.py` should match on `aliases` so a question about "Pellino" surfaces both pages, not just one.
