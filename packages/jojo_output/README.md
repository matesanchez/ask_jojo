# jojo_output

Rich output rendering. Phase 5 owns this package.

## Scope

- **Marp rendering.** Slide decks rendered with `@marp-team/marp-core` in a Web Worker inside the frontend; this package produces the Marp markdown.
- **matplotlib sandbox.** Generates plots from `jojo_qa` answers. Runs in a resource-limited sandbox: no network, allowlisted imports, capped memory and CPU.
- **docx / pptx / pdf generation paths.** Uses `python-docx`, `python-pptx`, and the `pdf` skill's patterns for clean professional output.
- **"File this" flow.** One-click persistence of generated outputs into `ask_jojo_wiki/outputs/` with citation provenance preserved.

## Invariants

- Every generated output cites the wiki pages it drew from.
- No arbitrary code execution — matplotlib runs sandboxed, with a fixed allowlist of imports.
- Outputs filed back into the wiki are always editable (no binary-only artifacts without a `.md` counterpart).

## Current state

Phase 0 skeleton. CLI stub only.

## References

- `ask_jojo/PLAN.md` §6 Phase 5.
