# ADR 0006 — `ask_jojo_raw` Privacy Invariant

- **Status:** Accepted
- **Date:** 2026-04-22
- **Deciders:** Mateo de los Rios (with Nurix legal review)
- **Supersedes:** —
- **Superseded by:** —

## Context

Nurix's legal and MSA review (completed 2026-04-22) cleared JoJo Bot v2.0 to ingest internal Protein Sciences corpus — SharePoint sites, OneDrive folders, NurixNet pages — into the `ask_jojo_raw` repository. The clearance is **conditional**: the raw corpus must remain in a private repository accessible only to authorized Nurix personnel. The derived wiki in `ask_jojo_wiki` is also private in the current phase, but the binding constraint from legal is on the raw layer specifically, because that is where primary source material with original permissions-at-ingest lives.

Without an explicit invariant and an ADR to point to, there is a foreseeable failure mode: someone in the future (a new contributor, an IT migration, a well-intentioned open-source push) flips visibility on the raw repo to share a sanitized subset, or to publish the project more broadly, and silently breaks the legal clearance. Recovery from that would involve notifying legal, auditing what was exposed while the repo was public, and potentially re-negotiating the MSA carve-out.

## Decision

`ask_jojo_raw` is permanently private. Its GitHub repository visibility must remain set to "Private" for the lifetime of the project. This is an invariant, not a default.

Operational consequences:

1. The README of `ask_jojo_raw` carries a visible notice at the top stating this invariant and pointing to this ADR.
2. Any attempt to change visibility to "Public" or to an organization-wide-readable setting requires (a) a new ADR that supersedes this one, and (b) a renewed legal review. Neither is sufficient alone.
3. The connector boundary continues to filter ingest to documents that a standard full-time Nurix employee can already read (the pre-existing all-FTE ACL model described in `ask_jojo_raw/README.md`). This ADR does not change that; it adds a hard floor beneath it.
4. When Phase 7b promotes the authoritative `ask_jojo_raw` clone to the shared Nurix-internal server, the same invariant applies to the server's Git remote. "Internal network only" is not equivalent to "private GitHub repo" — both conditions must hold independently.
5. The wiki layer (`ask_jojo_wiki`) is also private at ratification time, but this ADR does not constrain it. If a sanitized, citation-free derivative of the wiki ever needs to become public (e.g., a published process diagram), that is a separate decision.

## Alternatives Considered

**Rely on the README notice alone.** Insufficient. README notices get skimmed; repo visibility is a single-click action that happens in a different UI context entirely. The ADR creates a forcing function by requiring a documented trade-off before any change.

**Add a CI check that asserts repo visibility.** Possible but not in scope for Phase 0. The GitHub API exposes repo visibility via `gh api /repos/<org>/ask_jojo_raw --jq '.visibility'`. A future lint rule in `packages/jojo_lint/` could fail CI if the raw repo's visibility is ever anything other than `private`. This would be a defense-in-depth measure on top of the policy.

**Move the binding constraint into a contract with legal.** The MSA review already establishes this. The ADR captures it on the engineering side so that the policy lives where engineers look, not only in a contract document.

## Consequences

Positive:

- Legal clearance for ingest remains intact as long as the invariant holds.
- New contributors see the notice at the top of the raw repo's README and have a pointer into the reasoning.
- Future changes to the privacy posture require a superseding ADR, which forces the conversation to happen before the change.

Negative:

- The project cannot be trivially open-sourced. If that ever becomes desirable, the open-source path cannot include the raw layer.
- Tooling that assumes a public raw corpus (external auditors, published demos) will not work without a scrub-and-republish pipeline, which is not built.

Neutral:

- This ADR places no constraint on the wiki or the app repo. Both can be open-sourced independently if the product ever goes that direction, as long as the wiki's citations remain abstract enough to not leak raw content.

## References

- `ask_jojo_raw/README.md` — operational notice at top of file.
- `ask_jojo/docs/ADR/0002-three-repo-split.md` — architectural basis for the three-repo split.
- Nurix ↔ Anthropic MSA — controlling legal document (off-repo; stored with Legal).
