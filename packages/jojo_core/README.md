# jojo_core

Shared primitives used by every other `jojo_*` package. Phase 0 is skeleton only; populated progressively.

## Scope

When filled in, this package owns:

- **Config loading.** Reads `%APPDATA%\JojoBot\config.json` (DPAPI-encrypted per ADR 0004). Holds Anthropic API keys, Microsoft Graph credentials, NurixNet session cookies, Redis connection string. Single source of truth for secrets.
- **Anthropic client factory.** Thin wrapper around the Anthropic SDK that returns pre-configured clients per model tier (Haiku 4.5, Sonnet 4.6, Opus 4.6). Centralizes retry / rate-limit / model-routing policy so compile and lint don't reimplement it.
- **Logging.** Structured logging with rotation, levels driven by config. Ensures `jojo_ingest`, `jojo_compile`, and the backend all log in the same schema.
- **Path helpers.** Canonical accessors for the three repo clones (`ask_jojo/`, `ask_jojo_wiki/`, `ask_jojo_raw/`). Resolves from either the workspace root or `$env:JOJO_WORKSPACE_ROOT`.
- **Redis / RQ wiring.** Connection factories and worker-decorator conventions for background jobs.

## Current state

Phase 0 skeleton. CLI is a stub that prints a "not implemented yet" message and exits non-zero. Smoke test in `tests/` keeps pytest green for CI.

## Roadmap

- **Phase 1.** Config loader, logging, Anthropic client factory, path helpers.
- **Phase 2.** Subagent-spawn helpers for the absorb loop.
- **Phase 5.** Redis/RQ queues used by the rich-output pipeline.

## References

- `ask_jojo/PLAN.md` §3.3 Packages layout.
- `ask_jojo/docs/ADR/0003-packages-layout.md` — the decision to split subsystems into packages.
