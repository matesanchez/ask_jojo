# Path B — MSAL Device-Code Setup (A Dummy's Guide)

**Goal.** Replace the "paste a 60-minute Graph Explorer token into `JOJO_GRAPH_ACCESS_TOKEN`" dance with a one-time interactive login that keeps working unattended for ~90 days. This is what unblocks **scheduled** SharePoint ingest.

**Reading time:** ~15 minutes.
**Doing time:** ~30–45 minutes the first time, then never again.

**Prerequisites you already satisfy:**

- Your pasted token shows `Application.ReadWrite.All` + `DelegatedPermissionGrant.ReadWrite.All` + `Directory.ReadWrite.All` scopes, which means you personally can register a new app in the Nurix Entra tenant **without** opening an IT ticket.
- Your `wids` claim includes `b79fbf4d-3ef9-4689-8143-76b194e85509` (Application Developer role) — that's the directory role that lets you self-register.
- Python 3.11 and the rest of the JoJo Bot dev env (which you have, since the test suite is green).

---

## What's actually happening, in one paragraph

Device-code auth is the flow where a CLI prints "go to https://microsoft.com/devicelogin and enter code `ABC-123`, I'll wait." You do that in a browser, sign in as yourself (MFA and all), and the CLI comes back with a refresh token that lives ~90 days. MSAL (Microsoft's auth library) handles the refresh transparently: every time we call `acquire_token_silent`, MSAL checks its on-disk cache, sees the access token is expired, uses the refresh token to mint a new one, and hands it back. The connector never sees the difference. Unlike Path C (client-credentials / service-account), this flow acts as *you* — which is fine for V1 because you're the only operator.

---

## Step 1 — Register a new app in Entra

You're giving our ingest code its own identity separate from Graph Explorer. This keeps the blast radius small (if the token leaks, revoking this app doesn't log you out of Graph Explorer) and gives us a clean audit trail.

1. Go to **https://entra.microsoft.com** and sign in as `mdelosrios@nurixtx.com`.
2. Left nav → **Applications** → **App registrations** → **+ New registration**.
3. Fill in:
   - **Name:** `JojoBot Ingest (Local)`
   - **Supported account types:** **Accounts in this organizational directory only (Nurix Therapeutics only — Single tenant)**
   - **Redirect URI:** leave blank. Device-code flow doesn't use one.
4. Click **Register**.
5. On the app's overview page, copy and save:
   - **Application (client) ID** — a GUID, looks like `12345678-abcd-...`
   - **Directory (tenant) ID** — should be `1c966021-d551-45e4-89a5-849f81b69208` (the Nurix tenant)

## Step 2 — Enable the "public client" flow

Device-code is a **public client** flow, which means no client secret is stored. You have to tell Entra that explicitly.

1. From the app's page, left nav → **Authentication**.
2. Scroll down to **Advanced settings** → **Allow public client flows**.
3. Flip the toggle to **Yes**.
4. Click **Save** at the top.

## Step 3 — Add the Graph permissions

1. Left nav → **API permissions** → **+ Add a permission**.
2. Pick **Microsoft Graph** → **Delegated permissions**.
3. Check these (use the search box — you'll find them under *Sites*, *User*, *openid*):
   - `Sites.Read.All` — read every SharePoint site you can see.
   - `Sites.ReadWrite.All` — future-proofing; not used in Phase 1. Skip if you prefer minimum scope.
   - `User.Read` — auto-added; lets us echo "signed in as mdelosrios" on first run.
   - `openid`, `profile`, `offline_access` — the trio that makes refresh tokens work. **`offline_access` is the critical one** — without it, your refresh token dies with the session and Path B degrades to Path A.
4. Click **Add permissions**.
5. Back on the API permissions page, the table should now list the five scopes. The **Status** column probably says "Not granted" with a yellow warning.
6. Click **Grant admin consent for Nurix Therapeutics**. Your account has the rights to do this (confirmed by the `DelegatedPermissionGrant.ReadWrite.All` scope on your Graph Explorer token). Confirm in the popup.
7. All five should flip to green checkmarks.

## Step 4 — Install MSAL

```powershell
cd C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\ask_jojo
pip install "msal>=1.28"
```

Also add it to `pyproject.toml` under the `[project.optional-dependencies]` `cloud` extra so fresh checkouts pick it up automatically:

```toml
cloud = [
    "httpx>=0.27",
    "pytest-httpx>=0.30",
    "msal>=1.28",
]
```

## Step 5 — Wire `msal_device_code_provider` into `graph.py`

The existing `TokenProvider` abstraction is already the right shape for this — you just add a new factory alongside `env_token_provider`. Add this near the top of `packages/jojo_ingest/graph.py`, just after `env_token_provider`:

```python
import json
from pathlib import Path as _Path


def msal_device_code_provider(
    *,
    client_id: str | None = None,
    tenant_id: str | None = None,
    scopes: list[str] | None = None,
    cache_path: _Path | None = None,
    interactive: bool = True,
) -> TokenProvider:
    """Path B auth: MSAL device-code flow with on-disk token cache.

    On first call: prints a device-code prompt; you open the URL and enter the
    code; MSAL stashes an encrypted token cache at `cache_path`. On every
    subsequent call (this run or any future run), MSAL silently refreshes from
    the cache — typically ~90 days of unattended operation per interactive
    login, constrained by the tenant's conditional-access policy.

    Args read from env vars if not passed explicitly:
      - `JOJO_MSAL_CLIENT_ID`  — the Entra app registration's Application ID.
      - `JOJO_MSAL_TENANT_ID`  — the Nurix tenant ID.
      - `JOJO_MSAL_CACHE`      — defaults to %APPDATA%/JojoBot/tokencache.bin.

    `interactive=False` forces silent-only (useful in CI / scheduled tasks
    after the first login) — if no cached account is found, raises instead
    of blocking the process waiting on stdin.
    """
    import msal

    client_id = client_id or os.environ.get("JOJO_MSAL_CLIENT_ID", "").strip()
    tenant_id = tenant_id or os.environ.get("JOJO_MSAL_TENANT_ID", "").strip()
    if not client_id or not tenant_id:
        raise IngestError(
            "Path B needs JOJO_MSAL_CLIENT_ID and JOJO_MSAL_TENANT_ID set "
            "(see docs/ops/path-b-msal-device-code-setup.md)."
        )
    scopes = scopes or ["https://graph.microsoft.com/Sites.Read.All"]

    if cache_path is None:
        appdata = os.environ.get("APPDATA") or str(_Path.home() / ".jojo-bot")
        cache_path = _Path(appdata) / "JojoBot" / "tokencache.bin"
    cache_path = _Path(cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    cache = msal.SerializableTokenCache()
    if cache_path.exists():
        cache.deserialize(cache_path.read_text(encoding="utf-8"))

    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        token_cache=cache,
    )

    def _persist_cache() -> None:
        if cache.has_state_changed:
            cache_path.write_text(cache.serialize(), encoding="utf-8")

    def _get() -> str:
        # Try silent first — this is the hot path after the first login.
        accounts = app.get_accounts()
        result = None
        if accounts:
            result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            _persist_cache()
            return result["access_token"]

        # Cache miss / expired refresh token → fall back to device-code.
        if not interactive:
            raise IngestError(
                "Path B token cache is empty or expired, and interactive=False. "
                "Run `jojo-ingest login` once from an interactive terminal to seed the cache."
            )

        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise IngestError(f"MSAL initiate_device_flow failed: {json.dumps(flow)}")
        # MSAL's message includes the URL + code; print it so the user can see.
        print(flow["message"], flush=True)
        result = app.acquire_token_by_device_flow(flow)  # blocks until user completes or timeout
        if "access_token" not in result:
            raise IngestError(f"MSAL device_flow failed: {result.get('error_description', result)}")
        _persist_cache()
        return result["access_token"]

    return _get
```

Note the `interactive=False` kwarg — that's the knob that lets scheduled runs (Windows Task Scheduler) demand silent-only refresh and fail loudly rather than block on stdin if the cache ever empties.

## Step 6 — Update the factory to prefer Path B when configured

In `packages/jojo_ingest/sharepoint.py`, `build_sharepoint_connector_from_env` currently calls `env_token_provider()` unconditionally. Change the provider selection to:

```python
def _select_token_provider(token_override: str | None = None) -> TokenProvider:
    if token_override:
        return lambda _=token_override: _   # explicit CLI override beats everything
    if os.environ.get("JOJO_GRAPH_ACCESS_TOKEN"):
        return env_token_provider()           # Path A fallback
    if os.environ.get("JOJO_MSAL_CLIENT_ID") and os.environ.get("JOJO_MSAL_TENANT_ID"):
        return msal_device_code_provider(interactive=_is_interactive())
    raise SharePointEnvError(
        "No SharePoint auth configured. Set JOJO_MSAL_CLIENT_ID + JOJO_MSAL_TENANT_ID "
        "for Path B (recommended), or paste a token into JOJO_GRAPH_ACCESS_TOKEN for Path A."
    )


def _is_interactive() -> bool:
    import sys
    return sys.stdin is not None and sys.stdin.isatty()
```

Then use `_select_token_provider(token_override=token_override)` in the factory.

## Step 7 — Add a `jojo-ingest login` subcommand (seed the cache from a friendly prompt)

Don't make the user stumble into the device-code prompt mid-ingest. Add a dedicated subcommand to `packages/jojo_ingest/cli.py` that calls `msal_device_code_provider()` once and returns — that's your "first-run" step before the first scheduled ingest.

```python
def _cmd_login(args: argparse.Namespace) -> int:
    from jojo_ingest.graph import msal_device_code_provider
    provider = msal_device_code_provider(interactive=True)
    token = provider()   # blocks until device flow completes, seeds the cache
    print(f"Login successful. Token cache seeded at {os.environ.get('JOJO_MSAL_CACHE', '<default>')}.")
    print(f"Token preview: {token[:20]}... (length={len(token)})")
    return 0


# in _build_parser:
login = sub.add_parser("login", help="Seed the MSAL device-code token cache (first-run)")
login.set_defaults(func=_cmd_login)
```

## Step 8 — First-run walkthrough

Open a fresh PowerShell, export the new env vars, and seed the cache:

```powershell
$env:JOJO_MSAL_CLIENT_ID = "<client-id-from-Step-1>"
$env:JOJO_MSAL_TENANT_ID = "1c966021-d551-45e4-89a5-849f81b69208"

jojo-ingest login
```

You'll see something like:

```
To sign in, use a web browser to open the page https://microsoft.com/devicelogin
and enter the code A1B2C3D4E to authenticate.
```

Do that, sign in as yourself (MFA included), and close the tab when it says "You can now return to the application." The CLI prints `Login successful` and exits. You should now see a `tokencache.bin` file at `%APPDATA%\JojoBot\tokencache.bin`.

## Step 9 — Verify scheduled-mode works

From the same shell, unset `JOJO_GRAPH_ACCESS_TOKEN` (if set) and run a tiny SharePoint sync:

```powershell
Remove-Item Env:\JOJO_GRAPH_ACCESS_TOKEN -ErrorAction SilentlyContinue
$env:JOJO_SHAREPOINT_SITES = "https://nurix.sharepoint.com/sites/ProteinScience"

jojo-ingest sync sharepoint --raw C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\ask_jojo_raw
```

If it runs silently (no device-code prompt) and reports `added: N`, **you're done**. The cache worked. Path B is live.

To prove the cache survives a full reboot: close the shell, open a new one, re-`$env:`-set `JOJO_MSAL_*`, and re-run. Still silent? Congratulations, scheduled ingest is now unblocked.

## Step 10 — Persist the env vars so Task Scheduler can use them

Add the two `JOJO_MSAL_*` values to `%APPDATA%\JojoBot\config.json` (coming in the local-mode packaging pass — DPAPI-encrypted). For now, if you want to test Task Scheduler before that pass lands, set them as **user-level** environment variables:

```powershell
[Environment]::SetEnvironmentVariable("JOJO_MSAL_CLIENT_ID", "<client-id>", "User")
[Environment]::SetEnvironmentVariable("JOJO_MSAL_TENANT_ID", "1c966021-d551-45e4-89a5-849f81b69208", "User")
[Environment]::SetEnvironmentVariable("JOJO_SHAREPOINT_SITES", "<comma-separated-site-urls>", "User")
```

Open a new shell and `echo $env:JOJO_MSAL_CLIENT_ID` — if it echoes, Task Scheduler will also see it.

---

## Troubleshooting

### "AADSTS65001: The user or administrator has not consented to use the application"

Admin consent didn't take in Step 3.6, or you added scopes after consenting. Go back to **API permissions** → click **Grant admin consent for Nurix Therapeutics** again.

### "AADSTS70011: The provided request must include a 'scope' input parameter"

The `scopes` list is wrong. For delegated flows, scopes must be prefixed with the resource — i.e. `"https://graph.microsoft.com/Sites.Read.All"`, **not** `"Sites.Read.All"`. Double-check the `scopes` default in `msal_device_code_provider`.

### Device-code prompt re-appears every run

`offline_access` wasn't added in Step 3.3, so MSAL never got a refresh token, so every run falls back to interactive. Add it, admin-consent, delete `tokencache.bin`, run `jojo-ingest login` again.

### "AADSTS50059: No tenant-identifying information found"

`JOJO_MSAL_TENANT_ID` is empty or misspelled. Sanity-check with `echo $env:JOJO_MSAL_TENANT_ID`.

### Conditional-access kicks you out mid-session

Some Nurix tenants enforce MFA re-auth every N days. If you see an interactive prompt unexpectedly around the N-day mark, that's why. Re-run `jojo-ingest login` and you're good for another cycle. If it happens more often than monthly, talk to IT about a CA policy exception for this app.

### Token cache on a shared/roaming profile

If Mateo's AppData is on OneDrive (unlikely for `%APPDATA%` but worth checking), move the cache path out. Set `JOJO_MSAL_CACHE=C:\ProgramData\JojoBot\tokencache.bin` (requires write access, so first-run needs an elevated shell).

---

## What this unblocks

Once Path B is live, the next items in the Phase 1 closeout chain are:

1. **Windows Task Scheduler wrappers** — now they can run silently because `interactive=False` gives a clean fail-fast behavior if the cache ever expires.
2. **DPAPI-encrypted `config.json`** — move the two `JOJO_MSAL_*` env vars (and later secrets) from env vars into an encrypted file keyed to your Windows user, so they survive across shells without being visible to `Get-ChildItem Env:`.
3. **Phase 1 exit criterion's "unattended for a week" clause** — Path B removes the only structural blocker. The rest is just letting it run.

---

## Revisit when

- Tenant rolls out a conditional-access policy that shortens refresh-token lifetime significantly (< 30 days makes Path B painful).
- Phase 7b begins — the shared-server deployment can't use device-code because it's multi-user, so it graduates to Path C (client-credentials / certificate-backed).
- MSAL ships a major version bump (2.x) that changes the `PublicClientApplication` API; the provider is small enough to port, but update the pin.
