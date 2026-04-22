# jojo_connectors_common

Shared foundation for every ingest connector in `packages/jojo_ingest/`.

## Why a separate package?

Phase 2+ packages (`jojo_compile`, `jojo_qa`, `jojo_lint`) depend on the
**raw-entry interface**, not on the connectors themselves. Pulling the
interface out into its own package makes that dependency explicit: the compile
loop imports `jojo_connectors_common`, not `jojo_ingest`, so the absorb
pipeline keeps working even if a particular connector is unavailable.

## Contents

| Module | Responsibility |
| --- | --- |
| `base` | Abstract `Connector` class + `SourceEntry` / `ConnectorResult` dataclasses |
| `frontmatter` | YAML frontmatter spec (PLAN.md §6 Phase 1 fields), serialization, typed parse |
| `manifest` | `ask_jojo_raw/manifest.json` load/save with idempotent `upsert`, supersedence tracking |
| `hashing` | `canonical_sha256` for stable content hashes; `stable_id` for filesystem-safe IDs |
| `redaction` | Regex PII/PHI pre-pass (SSN, email, phone, patient-id, DOB, credit-card) |
| `ignore` | `.jojoignore` parser — gitignore-style filtering for ingest walks |

## Invariants

- **Frontmatter field set is closed.** Only fields listed in
  `FRONTMATTER_FIELDS` ship in raw files. Adding a new field is a schema-
  version bump plus a Phase 2 compatibility review.
- **Redaction is mandatory.** Every raw file passes through `redact_pii()`
  before hitting disk. Connectors never skip this.
- **Manifest is authoritative.** If a raw file exists on disk but isn't in the
  manifest, it will be ignored by compile and eventually lint-flagged for
  cleanup. Write to disk via the driver, not around it.

## References

- `ask_jojo/PLAN.md` §6 Phase 1 — governing spec for the raw layer
- `ask_jojo/schema/CLAUDE.md` §6 — compile-side consumer of the frontmatter
- `ask_jojo_raw/README.md` — directory layout in the raw repo
