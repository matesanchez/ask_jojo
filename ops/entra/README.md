# Entra app registration — portal-free path

Background on why this exists: some Nurix user accounts hit a 401 when
navigating to **App registrations** in the Azure Portal, even though the
account has every Microsoft Graph scope needed to register apps. The
error looks like:

```
{"sessionId":"...","subscriptionId":"","resourceGroup":"","errorCode":"401",...}
```

That's the Azure Portal trying to load subscription context that you
don't have — it's unrelated to your Entra permissions. Two workarounds:

1. Try [entra.microsoft.com](https://entra.microsoft.com/) → Applications
   → App registrations. The dedicated Entra admin portal doesn't require
   subscription context and often works where `portal.azure.com` 401s.

2. Run `Register-JojoBotApp.ps1` in this folder. It uses your Graph
   Explorer token to register the app, create its service principal,
   and self-consent the delegated scopes (`Sites.Read.All`,
   `offline_access`, `User.Read`) — no portal clicks at all. This is
   what the rest of this README walks through.

## Prerequisites

You need a Graph Explorer token whose `scp` claim includes:

- `Application.ReadWrite.All` — to create the application
- `Directory.ReadWrite.All` — to create the service principal
- `DelegatedPermissionGrant.ReadWrite.All` — to self-consent

Mateo's current consented scopes include all three, so he's covered.
Grab a fresh token from Graph Explorer's **Access token** tab —
tokens expire ~60 min after issue, so run the script soon after copying.

## Running it

```powershell
cd C:\Users\mdelosrios\Claude_Local\jojo_bot_v2.0\ask_jojo\ops\entra
.\Register-JojoBotApp.ps1 -Token "eyJ0eXAi..."
```

The script will:

1. Call `GET /me` to confirm whose token this is.
2. `POST /applications` with `isFallbackPublicClient = true` + a
   `publicClient.redirectUris = ["http://localhost"]` block (the
   placeholder MSAL device-code uses).
3. `POST /servicePrincipals` so the app exists in the tenant.
4. Look up the Microsoft Graph service principal in your tenant
   (needed as the `resourceId` for the consent grant).
5. `POST /oauth2PermissionGrants` with `consentType=Principal` +
   `principalId=<your user id>` + the three scopes. This is
   self-consent — it does **not** grant on behalf of the whole
   tenant, which is exactly what we want.

On success it prints the **Client ID** and the env-var assignments you
need to feed into Path B.

## After it runs

Set the env vars (one-time per shell, or via `SetEnvironmentVariable`
with `User` scope to persist them):

```powershell
$env:JOJO_MSAL_CLIENT_ID = "<printed client id>"
$env:JOJO_MSAL_TENANT_ID = "1c966021-d551-45e4-89a5-849f81b69208"
```

Then seed the MSAL token cache once:

```powershell
jojo-ingest login
```

You'll see a device-code prompt. Paste the code into the URL it gives
you, sign in as `mdelosrios@nurixtx.com`, and close the browser. The
cache at `%APPDATA%\JojoBot\tokencache.bin` now holds a refresh token
good for ~90 days of silent renewals.

Re-running `Run-ValidationSyncAll.ps1` from the `ops/validation/`
folder should now work without the token prompt.

## Re-running and idempotency

The script does **not** deduplicate on display name by design — if you
re-run it, you'll get a second app with the same name. That's
deliberate: if you run it twice by accident, the failure mode is "two
apps in Entra with the same name," which is visible and recoverable,
rather than "silently reconfigured the one that was there."

If you need a second app (e.g. for a dev tenant), pass
`-DisplayName "JoJo Bot (dev)"`.

## Cleanup

If you need to delete the app:

```powershell
# Using the same Graph token that created it:
Invoke-RestMethod -Method DELETE `
  -Uri "https://graph.microsoft.com/v1.0/applications/<object-id>" `
  -Headers @{ Authorization = "Bearer $Token" }
```

The service principal and permission grant delete automatically with
the application.

## Troubleshooting

### Preflight fails with "Token is missing required scopes"

The script decodes your token's `scp` claim before making any writes
and bails early if a required scope isn't present. The fix is always
the same: in Graph Explorer, click your profile → **Consent to
permissions**, consent to the missing scope, and grab a **fresh**
token (existing tokens don't pick up newly-consented scopes).

The three scopes the script needs are:
- `Application.ReadWrite.All`
- `Directory.ReadWrite.All`
- `DelegatedPermissionGrant.ReadWrite.All`

If clicking "Consent" pops a "Need admin approval" dialog instead of
granting, the tenant has a policy that restricts this scope to Global
Administrators. In that case a Global Admin has to run the script (or
register the app in the Entra admin portal at entra.microsoft.com).

### "Insufficient privileges to complete the operation" on application create

You somehow got past the preflight but still got a 403. This usually
means the Application Developer role was revoked between when you
consented to the scope and when the POST actually hit the server,
or the tenant has an additional authorization policy layered on top.
Contact a Global Admin.

### "Insufficient privileges" on the oauth2PermissionGrants POST

You have `Application.ReadWrite.All` but not
`DelegatedPermissionGrant.ReadWrite.All`. Consent to the latter from
Graph Explorer and re-run — the earlier steps are idempotent up to
that point (app + SP are already created; the script just needs the
grant step to succeed).

### The grant endpoint succeeds but `jojo-ingest login` still prompts for admin consent

Some tenants enforce "admin consent required" on `Sites.Read.All` at
the tenant-policy level, which overrides even a DelegatedPermissionGrant
write. If that's your tenant, ask a global admin to run the grant
(or to grant tenant-wide consent from the new app's page in the Entra
portal). The script printout includes the client ID they'll need.
