---
question_id: q-029
question: "Walk me through the protein request UX redesign arc from 2022 to 2025 — what changed and why?"
asked_by: mateo
asked_date: 2026-05-19
session_date: 2026-05-19
session_id: cowork-2026-05-19-029
route: wiki
route_decided_by: regex
candidate_slugs:
  - protein-request-ux-redesign
  - protein-request-submission
hops_followed:
  - protein-request-ux-redesign
  - protein-request-submission
raw_fallback_used: false
raw_entries_read: []
miss_logged: false
confidence: medium
filed_back: false
filed_back_path: null
schema_version: 0.1.0
---

## Answer

The protein request form and checkout workflow in [[delphi|Delphi]] underwent a series of documented redesigns between 2022 and 2025. Each phase addressed a different class of problem: initial form completeness and checkout accountability (2022), prototype feedback and display standards (2022-2023), automated status tracking and request lifecycle visibility (2024), and inventory location granularity and data export capabilities (2025) [[protein-request-ux-redesign|Protein Request UX Redesign Arc (2022-2025)]].

**2022: Initial form refinements and checkout formalization**

The first documented redesign, dated September 2022, targeted the request detail page structure. Changes included: adding Biotinylation checkbox fields, reorganizing the General Information section (moving "Need by Date," "ETA," and "Completion Date" to a single row), and adding new fields for "Requester," "Needed by Groups," and "Request ID #." Clone inventory links were introduced to reference existing clones, and terminology was standardized (changing "Clone Target Form" to "Protein Target Form") [[protein-request-ux-redesign|Protein Request UX Redesign Arc (2022-2025)]].

In November 2022 the protein checkout workflow was formalized. At that time, checkout operated on an honor system: requesters were responsible for checking out only protein allocated to their specific request. Once checked out, physical location tracking was lost but tube contents could be identified by barcode scanning through a desktop application (R288). Production timelines were also formalized: 6-9 weeks for baculovirus and mammalian systems from existing clones, 3-4 weeks for E. coli, and 9-12 weeks and 6-7 weeks respectively when clones did not yet exist [[protein-request-ux-redesign|Protein Request UX Redesign Arc (2022-2025)]].

In parallel, Jose Santos produced revised workflow documentation (June 2022) distinguishing protein re-supply scenarios (Case 1: existing clones and optional biomass) from novel protein requests (Case 2: new target systems with available clones). This introduced the concept of clone task grouping by request ID to avoid visual duplication and enable cross-request clone reuse tracking [[protein-request-ux-redesign|Protein Request UX Redesign Arc (2022-2025)]].

**2022-2023: Figma mockup reviews and display standards**

Two Figma review sessions (November 2022, January 2023) involving Jose Santos, Hugo Bousquet, and Emily Low produced detailed feedback on prototype designs. Decisions from this phase included: removing cap-color columns (clone tubes do not have colored caps), standardizing units (from molar to mass-based units such as ng/uL), and correcting the Biomass Inventory table to show culture volume in liters. The reviews also led to decisions that Protein Inventory should display only Protein ID, total nmoles remaining, and concentration, and that picklist labels should be explicitly marked ("Clone Picklist," "Biomass Picklist," "Protein Picklist") [[protein-request-ux-redesign|Protein Request UX Redesign Arc (2022-2025)]].

**2024: Automated status tracking and homepage redesign**

In March 2024, Emily Low designed a complete redesign of the Protein Production Requests homepage table. The principal change was replacing manual "Internal Status" and "Completion Date" fields with automated status pills driven by downstream task state changes. Each status pill populates automatically when a trigger event occurs and links directly to the corresponding task detail page. The six status pills are: Clone Registration, Small Scale Expression/Purification, Large Scale Expression, Large Scale Purification, and Request Complete [[protein-request-ux-redesign|Protein Request UX Redesign Arc (2022-2025)]]. This automated tracking approach was carried forward into the current protocol [[protein-request-submission|Protein Request Submission]].

Also in March 2024, Hugo Bousquet consolidated submission requirements into a workflow checklist that formalized BirA selection procedures, mandatory field requirements for the Large Scale Expression Task, and the constraint that biotinylation intent must be specified at request initiation — changing it mid-workflow requires canceling the request and creating a new one [[protein-request-ux-redesign|Protein Request UX Redesign Arc (2022-2025)]].

**2025: Inventory location granularity and ML export**

In March 2025, Aaron Moranville and Emily Low proposed refined changes to the inventory checkout interface. The checkout table was reorganized by moving the Barcode column to the end and introducing new columns for Storage Rack, Rack ID, and Rack Position, enabling hierarchical physical location specification beyond the previous free-form Location string. The motivation was that existing location tracking was insufficiently granular for Nurix's distributed freezer infrastructure [[protein-request-ux-redesign|Protein Request UX Redesign Arc (2022-2025)]].

In May 2025, Emily Low filed a request for a one-time export of protein production data for machine learning model training. The export schemas specified fields including Task ID, Clone ID, Project, Clone Target Form, Expression System, Soluble Expression Level, Starting AA, Ending AA, and Protein Sequence (for small-scale tasks), and Project, Target, Protein Target Form, Protein ID, Status, Tm APO, Protein Yield, Final Sequence, Starting AA, and Ending AA (for large-scale tasks). The request highlighted that protein sequence data was not yet included in standard Delphi export features [[protein-request-ux-redesign|Protein Request UX Redesign Arc (2022-2025)]].

**Design principles that emerged across the arc**

Across all phases, five consistent principles emerged: (1) automated status tracking replaced manual status updates; (2) hierarchical location specification replaced free-form text; (3) picklist types were labeled explicitly; (4) biotinylation intent became a request-level commitment with restricted mid-workflow modification; and (5) export capabilities expanded progressively to support external tool integration including machine learning model training [[protein-request-ux-redesign|Protein Request UX Redesign Arc (2022-2025)]].

## Sources

- `protein-request-ux-redesign` — primary decision page; covers the full 2022-2025 redesign arc with dated artifacts and stated motivations for each phase.
- `protein-request-submission` — protocol page; documents the current (post-2024) protein request submission procedure, incorporating the automated status pill approach from the 2024 redesign.

## Confidence

Medium confidence. All named features, design decisions, dates, and motivations are extracted from `protein-request-ux-redesign`, which cites dated source artifacts from Jose Santos, Hugo Bousquet, Emily Low, and Aaron Moranville. No feature names are invented.

The 2025 inventory checkout refinements and the May 2025 export request are described as "proposed" in the wiki — their implementation status in Delphi is not confirmed in the absorbed sources.

## Follow-ups

1. Were the March 2025 inventory checkout table changes (Storage Rack, Rack ID, Rack Position) implemented in a specific ACS release — if so, which one?
2. Was the May 2025 one-time protein production export request fulfilled, and were the resulting datasets used for ML model training?
3. Is there a 2026 addition to this redesign arc in progress — for example, further sequence data integration or additional export capabilities?

## Filed back?

No. The answer synthesizes the existing wiki decision page without novel content.

## Session notes

This is a hard-difficulty question that requires tracing a multi-year arc from a single decision page with extensive detail. The answer follows the chronological structure of the source page. The key discipline is not inventing feature names (the UX changes are described with the same names used in the source artifacts). The `protein-request-submission` page grounds the current-state protocol; the `protein-request-ux-redesign` page explains how the current state was reached.
