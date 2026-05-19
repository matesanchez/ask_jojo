---
question_id: q-020
question: "What is IRF5's role in autoimmune disease, and how was the Nurix DEL screen for it structured?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-020
route: wiki
route_decided_by: regex
candidate_slugs:
  - irf5
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

**IRF5 in Autoimmune Disease** [[irf5|IRF5 Target]]

IRF5 (Interferon Regulatory Factor 5) is a transcription factor expressed primarily in dendritic cells, macrophages, and lymphocytes. It functions downstream of pattern recognition receptor (PRR) signaling as a central regulator of proinflammatory cytokine production. PRR activation leads to K63 ubiquitylation and phosphorylation of IRF5, which drives nuclear translocation and transcription of proinflammatory cytokine genes [[irf5|irf5]].

IRF5 is implicated in the pathogenesis of systemic lupus erythematosus (SLE), rheumatoid arthritis (RA), and inflammatory bowel disease (IBD). Nurix targeted IRF5 for a CTM hook for selective IRAK4 CTM development — meaning an IRF5-binding ligand was being pursued as a potential component of an IRAK4-targeting degrader [[irf5|irf5]].

**Domain Organization** [[irf5|IRF5 Target]]

(Residue numbering based on isoform 2):
- DBD (DNA-binding domain): highly conserved; binds DNA consensus sequence 5'-AACCGAAACTAA-3'
- ID (regulatory domain): contains nuclear localization signal (NLS) and nuclear export signal (NES); controls nuclear translocation
- TAD/IAD (transactivation domain including Interferon Association Domain and Serine Rich Region): mediates IRF5 dimerization and co-factor interactions; undergoes phosphorylation-dependent conformational changes; contains the K63-ubiquitylation site
- CTD/AID (C-terminal auto-inhibitory domain)

IRF5's closest paralog is IRF6, which was used as a counterscreen target. IRF5 p150 isoform dimerizes upon activation [[irf5|irf5]].

**DEL Screen Structure** [[irf5|IRF5 Target]]

Five DEL campaigns (C1-C5) were conducted. The central strategy used multiple IRF5 target forms to capture both the inactive monomer and active dimer conformations, with IRF6 counterscreens to identify selective IRF5 binders.

Target forms used:
| Alias | Construct | Notes |
|---|---|---|
| His-Avi-IRF5 TAD DD monomer | 6H-TEV-Avi-Thr-IRF5(248-493;S456D,V336D) | Dimer-breaking mutations (monomer) |
| His-Avi-IRF6 TAD DD monomer | 6H-TEV-Avi-Thr-IRF6(196-445;S416D,V297D) | Counterscreen (monomer) |
| IRF5-Avi FL dimer | IRF5(1-514)-Avi-TEV-FLAG | Wild-type dimer |
| IRF6-Avi FL dimer | IRF6(1-467)-Avi-TEV-FLAG | Counterscreen dimer |
| His-Avi-IRF5 TAD DDDD Dimer | 6H-TEV-Avi-Thr-IRF5(248-493;S451D;S453D;S456D;S462D) | Phosphomimetic dimer |

**Key Supplements and Probe Affinities** [[irf5|IRF5 Target]]

- N5-1 peptide (NLS-derived): Kd = 99 nM by SPR against TAD monomer; binds TAD, likely stabilizes the inactive conformation.
- IRF5-CPP2/4/5 peptides (Helix 2/5 sequences): Kd ~0.5 µM by TR-FRET; disrupt dimerization.
- KD207 peptide (Hlx5-connector): IC50 ~12 µM by FP/FRET; binds full-length dimer; binding site uncertain.
- DNA duplex KD123 (5'-ATCGGAAAGGGAAACCGAAACTGAAGCC-3'): DBD probe; Kd ~0.84 µM.

**Screen Buffer and Personnel**

DEL screen buffer: cytosolic pH 7.2, 0.1 mM TCEP, 0.02% Tween 20, 1.0 mg/mL blocking DNA. Biology Lead: Ya-Wen Lu. Chemistry Lead: Emily Low. DEL Lead: Herman Yuen. DEL Scientists: Marcella Gilmore (C1-C3), Bill Sonnenburg (C4-C5) [[irf5|irf5]].

## Sources

- `irf5` — IRF5 target page; covers autoimmune disease indication, domain organization, five DEL campaigns, target forms with construct details, supplement probe affinities, and personnel. Source: IRF5 TR&DSP 20220331 (Emily Low, Ya-Wen Lu, updated by Bill Sonnenburg).

## Confidence

All claims are EXTRACTED from the `irf5` target page. The page is rated `confidence: medium` with a single source document. The five-campaign DEL structure, target form constructs, and supplement affinities are well-documented on the page. The connection between IRF5 and IRAK4 CTM development (IRF5 as a CTM hook for IRAK4) is stated on the page but not elaborated; the mechanism of this connection is not explained in the wiki. Confidence: medium.

## Follow-ups

1. How did the IRF5 DEL screening relate to the IRAK4 CTM program — was an IRF5 ligand ultimately used as the hook warhead in an IRAK4-targeting degrader?
2. What were the outcomes of the five DEL campaigns (C1-C5) — were confirmed hits identified and resynthesized?
3. Is there a downstream IRF5 program page, or does the target page represent the complete captured record?

## Filed back?

No. The answer summarizes the existing wiki page without novel content.

## Session notes

This is a complex DEL-screen-strategy question with multiple construct variants and supplement affinities. The discriminating details are: five campaigns (C1-C5), the phosphomimetic dimer construct (DDDD mutations), the N5-1 peptide Kd = 99 nM, and the cytosolic buffer pH 7.2. Hallucinated construct residue ranges or affinity values are fails. The IRF5-IRAK4 CTM-hook relationship is a notable biological connection that a correct answer should surface.
