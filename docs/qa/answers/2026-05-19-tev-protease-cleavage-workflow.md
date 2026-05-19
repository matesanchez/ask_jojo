---
question_id: q-034
question: "What is the TEV protease cleavage workflow, and when is it used in protein purification?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-034
route: wiki
route_decided_by: regex
candidate_slugs:
  - tev-protease-purification
hops_followed:
  - tev-protease-purification
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: low
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

**Purpose**

TEV (Tobacco Etch Virus) protease cleavage is used to remove affinity purification tags from recombinant proteins after initial affinity chromatography. The most common scenario is removing a His-TEV tag from a protein that was expressed with that tag to enable nickel-NTA (Ni-NTA) affinity capture. Downstream assays — including surface plasmon resonance (SPR), crystallography, and some cell-based assays — may require tag-free protein, motivating the cleavage step [[tev-protease-purification|TEV Protease Cleavage and Purification]].

TEV protease cleavage is incorporated into protein production workflows at Nurix as documented in Isabel Morgado's archive (14 entries spanning 2021-2024) [[tev-protease-purification|TEV Protease Cleavage and Purification]].

**Recognition sequence**

TEV protease recognizes and cleaves the sequence ENLYFQ-G/S, with cleavage occurring between the glutamine (Q) and the following residue (typically G or S). The expression construct must be designed with a TEV recognition site between the affinity tag and the target protein's N-terminus for this workflow to apply [[tev-protease-purification|TEV Protease Cleavage and Purification]].

**Workflow steps**

1. The target protein is expressed as a His-TEV-tagged fusion and captured by Ni-NTA affinity chromatography (initial purification).
2. The affinity-captured protein is incubated with recombinant TEV protease. Cleavage liberates the native protein N-terminus while the His-TEV tag remains on the cleaved fragment.
3. The cleavage mixture is subjected to a polishing step to remove the cleaved tag fragment, uncleaved protein, and TEV protease. The standard polishing step is Ni-NTA re-capture (the tag-bearing fragment, uncleaved His-tagged protein, and His-tagged TEV protease all bind the resin; the tag-free target protein flows through). An alternative polishing step documented in Isabel's archive is Strep-tag chromatography, used when the native protein lacks His residues but carries a Strep tag for downstream use [[tev-protease-purification|TEV Protease Cleavage and Purification]].

**When it is used**

TEV cleavage is applied when affinity tag removal is required for downstream applications. Contexts documented in the wiki include SPR, crystallography, and production workflows where the tag would interfere with assay readout. The His-TEV system is the predominant implementation in Isabel's archive, with specific cross-references to constructs including NECC-N00662, 3ZSU, and NRAS/KRAS constructs [[tev-protease-purification|TEV Protease Cleavage and Purification]].

**Cleavage efficiency and optimization**

TEV cleavage efficiency can be incomplete, leaving a fraction of protein uncleaved (still bearing the His-TEV tag). This is particularly problematic for downstream assays requiring tag-free protein. Reaction conditions — protease concentration, incubation temperature, buffer pH, reaction duration — should be empirically optimized per construct. Detailed empirical parameters from Isabel's archive are not yet fully absorbed into the wiki page [[tev-protease-purification|TEV Protease Cleavage and Purification]].

## Sources

- `tev-protease-purification` — primary method page; covers the purpose, TEV recognition sequence (ENLYFQ-G/S), workflow steps (affinity capture, cleavage, Ni-NTA or Strep-tag polishing), use cases, and cleavage efficiency caveats. **Confidence:low.**

## Confidence

Low confidence, matching the source page's own confidence:low. The workflow description (recognition sequence, Ni-NTA polishing, Strep-tag alternative) is sourced from `tev-protease-purification`. Detailed reaction conditions (specific protease concentrations, temperatures, durations) for individual constructs are not yet captured in the wiki page and would require accessing Isabel Morgado's full archive.

The ENLYFQ-G/S sequence (as stated in the wiki) is the canonical TEV site and is consistent with established literature; this is one case where the wiki value and widely known biochemistry agree.

## Follow-ups

1. What TEV protease concentration and reaction temperature does Nurix use as the starting point before construct-specific optimization?
2. For which target constructs has TEV cleavage been found to be chronically inefficient, requiring alternative tag-removal strategies?
3. Is His-tagged TEV protease the standard reagent at Nurix, and is it produced in-house or purchased?

## Filed back?

No. The answer reflects the existing wiki page content.

## Session notes

This is an easy-category question with a single primary page. The answer correctly notes that the `tev-protease-purification` page's confidence:low status stems from the source being a partially absorbed archive, not from doubt about the method's existence or general workflow. The ENLYFQ-G/S sequence (not ENLYFQ/S as in the task brief) matches the wiki value exactly and is used here.
