# jojo_ingest

Source connectors that populate `ask_jojo_raw/`. Phase 1 owns this package.

## Scope

- **SharePoint connector.** MS Graph OAuth, walks sites → document libraries → files, converts Office formats to markdown, records ACLs and source URLs. Scopes: `Files.Read.All`, `Sites.Read.All`.
- **OneDrive connector.** User-scoped Graph calls; same conversion pipeline.
- **NurixNet connector.** Playwright persistent-context session, SSO cookie, crawl with `trafilatura` first / Playwright fallback. Images download locally.
- **Drive connector.** SMB + local-path fallback, `watchdog` for change detection, Office lock-file handling.
- **Upload endpoint.** "Upload to raw" button in the UI drops into the same ingest pipeline.

Each connector takes a `--since <iso-date>` flag for incremental sync. Schedules: SharePoint 4h · OneDrive 24h · NurixNet weekly · Drive 24h.

## Invariants

- One raw file = one logical source entry.
- Ingest is idempotent (same SHA256 = no new file).
- Versioning without overwrite (new versions alongside old; supersedence in manifest).
- Mandatory YAML frontmatter on every raw file (see PLAN.md §6 Phase 1).
- Pre-LLM regex redaction for PII/PHI before anything else.
- `ask_jojo_raw/manifest.json` is the mechanical source of truth.

## Current state

Phase 0 skeleton. CLI stub only.

## References

- `ask_jojo/PLAN.md` §6 Phase 1.
- `ask_jojo_raw/README.md` — immutability invariants.
- `ask_jojo/docs/ADR/0006-raw-repo-privacy-invariant.md` — the raw repo stays private.
