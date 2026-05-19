---
question_id: q-016
question: "What do the mouse genetics say about Pellino-1 versus Pellino-2 in tumor immunity, and how did that shape the Pellino-1 program?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-016
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

The mouse genetic data is the primary evidence base for the Pellino-1 program's targeting rationale. It cleanly dissects Peli1 and Peli2 in vivo: Peli1 drives the anti-tumor immune phenotype; Peli2 does not.

**Peli1-/- mice** [[pellino-1|Pellino-1 Program]]

In the TC-1 syngeneic tumor model, Peli1-knockout mice showed statistically significant tumor growth inhibition (TGI, p<0.0001 vs. wild-type). In the MC38 model, Peli1-/- mice showed improved overall survival compared to wild-type controls. These results establish that Peli1 is necessary for suppressing the anti-tumor immune response in mice [[pellino-1|pellino-1]].

**Peli2-/- mice** [[pellino-1|Pellino-1 Program]]

Peli2-knockout mice showed no tumor growth inhibition in the TC-1 model. They showed no ex vivo T-cell hyperactivation phenotype. They showed no slowed tumor growth in the MC38 model [[pellino-1|pellino-1]]. This is a negative result across all three readouts, directly contrasting with Peli1-/-.

**Double-KO design rationale**

The 2019 medicinal-chemistry plan for the program included an explicit comparison of Peli1-KO, Peli2-KO, and Peli1+Peli2 double-KO mice in TGI models, specifically to decide whether selective Peli1 or pan-Pellino targeting was the right approach for the drug program. The double-KO arm was the uncertainty-resolution experiment [[pellino-1|pellino-1]].

**How this shaped the program**

The clean Peli2-/- negative result answered the strategic question: Peli1, not Peli2, is the driver of anti-tumor immune activity in mice. This supported advancing a Peli1-targeted degrader as the primary strategy. However, the lead CTM compound NRX-0393000 was subsequently confirmed to be a pan-Pellino degrader — it degrades both Peli1 and Peli2 (Peli2 DC50 = 1.4 nM confirmed by HiBiT). The wiki notes this as "making the compound a pan-Pellino degrader" without recasting the program's named target, which remains Pellino-1 [[pellino-1|pellino-1]]. The pan-Pellino degradation is documented as a chemical property of the lead, not a strategic redirection.

**Pellino family context** [[pellino-1-target|Pellino-1 Target]]

Peli1 (418 amino acids) and Peli2 (420 amino acids) share 82% sequence identity. Peli3a/3b share 71% identity with Peli1. The high identity between Peli1 and Peli2 is the structural basis for why selective inhibition or selective degradation is chemically challenging, and why the double-KO experiment was needed to resolve the biology question at the mouse-genetic level rather than the chemistry level [[pellino-1-target|pellino-1-target]].

Biochemically, Peli2 shows higher affinity for the pIRAK1 pT141 peptide (Kd 0.18 µM) than Peli1 (Kd 0.77 µM), suggesting Peli2 may be more active in IRAK1-dependent signaling [[pellino-1-target|pellino-1-target]], which is consistent with the lack of Peli2 contribution to the T-cell anti-tumor phenotype (T-cell signaling through Peli1 appears to be the relevant axis).

## Sources

- `pellino-1` — program page; covers Peli1-/- TGI data, Peli2-/- negative results, double-KO design, NRX-0393000 pan-Pellino activity.
- `pellino-1-target` — target page; covers Pellino family sequence identities, Peli2 pIRAK1 affinity data.

## Confidence

High-confidence claims: Peli1-/- TC-1 TGI (p<0.0001), Peli2-/- no TGI in TC-1 or MC38, NRX-0393000 Peli2 DC50 = 1.4 nM, Peli1/Peli2 82% sequence identity. All EXTRACTED from the program and target pages. The inference connecting Peli2's higher pIRAK1 affinity to the absence of T-cell anti-tumor phenotype is INFERRED and marked as such. Confidence: medium (inference present; program page is medium confidence).

## Follow-ups

1. Was the Peli1+Peli2 double-KO arm of the 2019 experiment actually executed, and if so, what was the result — i.e., did double-KO recapitulate or exceed Peli1-KO?
2. The pan-Pellino degradation of NRX-0393000 — did selectivity vs. Peli2 ever become a go/no-go criterion for clinical candidate selection?
3. Are there ex vivo data from Peli2-/- T cells that complement the in vivo TGI finding?

## Filed back?

No. All content is present in the two cited pages; the pIRAK1 affinity inference is marked INFERRED and should not be filed back without a decision page to confirm it.

## Session notes

This is the companion question to q-002 (Weiss lab Peli2 redundancy). Where q-002 focuses on the Jurkat cell-biology finding, q-016 focuses on the in vivo mouse genetics that resolved the Peli1 vs. Peli2 question. Together they stress-test whether the system can distinguish the cell-biology layer from the program/strategy layer on the same topic.
