# Redis Setup

JoJo Bot v2.0 uses Redis as the broker for RQ (Python job queue). Connectors, absorb runs, lint sweeps, and rich-output jobs all go through RQ so the FastAPI request cycle never blocks on Claude calls.

## Dev mode (any OS with Docker)

```bash
cd ask_jojo
docker compose up -d
docker exec -it jojo_redis redis-cli ping   # -> PONG
```

That's it. The compose file persists data under a named volume (`jojo_redis_data`) so restarts don't wipe the queue. Backend connects at `redis://localhost:6379/0` by default; override via `JOJO_REDIS_URL` in `%APPDATA%\JojoBot\config.json`.

## Production mode (Windows, local-first per ADR 0004)

Production deployments run as a local `.exe` on a user's Windows workstation. Docker Desktop is not a supportable dependency for that target — too much footprint, too much IT friction. Use **Memurai** instead, which is a Windows-native Redis fork maintained by the Redis company.

### Install

1. Download the Memurai Developer edition from https://www.memurai.com/get-memurai (free for development and internal use; paid for commercial production).
2. Run the installer. Default install puts the service at `C:\Program Files\Memurai\` and starts it as a Windows service listening on `127.0.0.1:6379`.
3. Verify:
   ```powershell
   & "C:\Program Files\Memurai\memurai-cli.exe" ping
   # -> PONG
   ```
4. The service is configured to start at boot. No manual intervention needed after the smoke-test succeeds.

### Configuration

The backend reads its Redis URL from `%APPDATA%\JojoBot\config.json` (DPAPI-encrypted per ADR 0004):

```json
{
  "redis_url": "redis://127.0.0.1:6379/0"
}
```

Binding to `127.0.0.1` (not `0.0.0.0`) keeps Memurai off the network. In local-first mode, the queue is single-tenant and never needs to answer external clients. Phase 7b (shared server) revisits this — when Redis runs on an internal VM, it gets a bound internal address + auth token.

### Persistence

Memurai supports Redis's AOF (append-only file) and RDB snapshot mechanisms. The JoJo Bot workload is small (job metadata, not document data), so default settings are fine: AOF on, snapshot every 60s if ≥ 1 key changed.

### Password / auth

For local-first mode, skip the Redis password — the 127.0.0.1 bind is sufficient. If IT or security asks for a password anyway, set it via `requirepass` in `memurai.conf` and update `redis_url` to `redis://:<password>@127.0.0.1:6379/0`. Store the password alongside the other DPAPI-encrypted secrets.

## Connecting from Python

The RQ wiring lives in `packages/jojo_core/` (populated in Phase 1). Workers are started via:

```bash
rq worker --url redis://localhost:6379/0 jojo-ingest jojo-compile jojo-lint
```

One worker per queue keeps failures isolated; the ingest worker crashing won't stall the compile queue.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ConnectionRefusedError` | Redis/Memurai not running | `docker compose up -d` (dev) or `Start-Service memurai` (prod) |
| Data lost after restart | AOF not enabled | Dev: already handled by compose. Prod: `appendonly yes` in `memurai.conf` |
| Jobs pile up | No worker attached | Start an `rq worker` for the queue in question |
| High memory | No eviction policy | For JoJo's workload this shouldn't happen — investigate before adding eviction |

## References

- `ask_jojo/PLAN.md` §3 — architectural context for the RQ-based job queue.
- `ask_jojo/docs/ADR/0004-local-first-deployment.md` — why local `.exe` rather than a dev-cluster-style stack.
- Memurai docs: https://docs.memurai.com
- RQ docs: https://python-rq.org
