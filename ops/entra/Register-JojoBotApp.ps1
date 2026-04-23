<#
.SYNOPSIS
    Register the JoJo Bot Entra app via Microsoft Graph (portal-free).

.DESCRIPTION
    Some users hit a 401 when navigating to App registrations in the Azure
    Portal even though their account has every permission needed to register
    apps. The portal is trying to load subscription context that doesn't
    apply to Entra-only users. This script sidesteps the portal by calling
    Microsoft Graph directly with a pasted Graph Explorer token.

    Creates:
      1. An Application object (public client — for MSAL device-code).
      2. Its Service Principal in the tenant.
      3. A delegated oauth2PermissionGrant to yourself for Sites.Read.All
         + offline_access + User.Read, so Path B can sign in silently
         after the first device-code interaction.

.PARAMETER Token
    Bearer token from Graph Explorer (Access token tab). Must include
    Application.ReadWrite.All, Directory.ReadWrite.All, and
    DelegatedPermissionGrant.ReadWrite.All in its scp claim.

.PARAMETER DisplayName
    The app's display name in Entra. Defaults to "JoJo Bot (MSAL device-code)".

.PARAMETER TenantId
    Nurix tenant GUID. Defaulted so you don't have to pass it.

.EXAMPLE
    .\Register-JojoBotApp.ps1 -Token "eyJ..."

.EXAMPLE
    # Override the display name if you already have one app registered:
    .\Register-JojoBotApp.ps1 -Token "eyJ..." -DisplayName "JoJo Bot (v2 device-code)"

.NOTES
    - The token expires ~60 minutes after it was issued; run the whole
      script within that window or re-paste.
    - If you've already created the app and just need the IDs, grep the
      previous run's output — the script doesn't deduplicate on display
      name by design (it fails loudly if you re-run, so you don't end up
      with two apps named the same thing silently).
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$Token,

    [string]$DisplayName = "JoJo Bot (MSAL device-code)",

    [string]$TenantId = "1c966021-d551-45e4-89a5-849f81b69208"
)

$ErrorActionPreference = "Stop"

# ---- constants -----------------------------------------------------------
# Microsoft Graph service principal — the well-known appId every tenant
# has for Graph. Delegated permission grants need both the client SP
# (our new app) and the resource SP (Graph).
$GraphAppId = "00000003-0000-0000-c000-000000000000"

# Delegated permission IDs on Microsoft Graph. These are stable GUIDs:
# https://learn.microsoft.com/en-us/graph/permissions-reference
$Scope_UserRead        = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"
$Scope_OfflineAccess   = "7427e0e9-2fba-42fe-b0c0-848c9e6a8182"
$Scope_SitesReadAll    = "205e70e5-aba6-4c52-a976-6d2d46c48043"

# Space-separated list sent into oauth2PermissionGrants.scope.
$GrantedScopes = @("User.Read", "offline_access", "Sites.Read.All") -join " "

$headers = @{
    Authorization  = "Bearer $Token"
    "Content-Type" = "application/json"
}

function Write-Section($title) {
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host " $title" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
}

function Invoke-Graph([string]$Method, [string]$Url, $Body) {
    $args = @{
        Method  = $Method
        Uri     = $Url
        Headers = $headers
    }
    if ($Body) { $args["Body"] = ($Body | ConvertTo-Json -Depth 10) }
    try {
        return Invoke-RestMethod @args
    } catch {
        # Graph 4xx responses include a helpful JSON body; surface it.
        $resp = $_.Exception.Response
        $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
        $detail = $reader.ReadToEnd()
        Write-Host "[graph error] $Method $Url" -ForegroundColor Red
        Write-Host $detail -ForegroundColor Red
        throw
    }
}

# ---- 0. preflight: check who I am ---------------------------------------
Write-Section "Preflight: confirming token identity"
$me = Invoke-Graph -Method GET -Url "https://graph.microsoft.com/v1.0/me"
Write-Host "Signed in as: $($me.userPrincipalName) ($($me.displayName))" -ForegroundColor Green
Write-Host "User object id: $($me.id)"
$UserId = $me.id

# ---- 1. create the application ------------------------------------------
Write-Section "Creating application '$DisplayName'"
$appBody = @{
    displayName           = $DisplayName
    signInAudience        = "AzureADMyOrg"       # single-tenant (Nurix only)
    isFallbackPublicClient = $true                 # enable public-client flows
    publicClient = @{
        # MSAL device-code does not actually use the redirect URI for network
        # I/O, but Entra requires one to mark the app as a valid public client.
        # "http://localhost" is the standard placeholder for device-code apps.
        redirectUris = @("http://localhost")
    }
    requiredResourceAccess = @(
        @{
            resourceAppId = $GraphAppId
            resourceAccess = @(
                @{ id = $Scope_UserRead;      type = "Scope" },
                @{ id = $Scope_OfflineAccess; type = "Scope" },
                @{ id = $Scope_SitesReadAll;  type = "Scope" }
            )
        }
    )
}
$app = Invoke-Graph -Method POST -Url "https://graph.microsoft.com/v1.0/applications" -Body $appBody
Write-Host "[ok] App created."
Write-Host "     displayName: $($app.displayName)"
Write-Host "     appId (client id): $($app.appId)" -ForegroundColor Green
Write-Host "     object id: $($app.id)"
$ClientId = $app.appId

# ---- 2. create the service principal ------------------------------------
# Apps are just definitions. To be usable in the tenant (including for
# permission grants), you need a matching service principal.
Write-Section "Creating service principal"
$spBody = @{ appId = $ClientId }
$sp = Invoke-Graph -Method POST -Url "https://graph.microsoft.com/v1.0/servicePrincipals" -Body $spBody
Write-Host "[ok] Service principal created. Object id: $($sp.id)"
$ClientSpId = $sp.id

# ---- 3. look up the Microsoft Graph service principal -------------------
Write-Section "Resolving Microsoft Graph service principal"
$graphSp = Invoke-Graph -Method GET `
    -Url "https://graph.microsoft.com/v1.0/servicePrincipals?`$filter=appId eq '$GraphAppId'"
$ResourceId = $graphSp.value[0].id
Write-Host "[ok] Microsoft Graph SP id: $ResourceId"

# ---- 4. self-consent to the delegated scopes ----------------------------
# Writing an oauth2PermissionGrant with consentType='Principal' + our own
# principalId is the mechanical equivalent of clicking "Grant consent" in
# the portal for just ourselves. It does NOT grant on behalf of the whole
# tenant — other users would still see a consent prompt on first sign-in.
# That's deliberate: we only need it working for Mateo's scheduled runs.
Write-Section "Granting delegated consent to self"
$grantBody = @{
    clientId    = $ClientSpId
    consentType = "Principal"
    principalId = $UserId
    resourceId  = $ResourceId
    scope       = $GrantedScopes
}
$grant = Invoke-Graph -Method POST -Url "https://graph.microsoft.com/v1.0/oauth2PermissionGrants" -Body $grantBody
Write-Host "[ok] Granted scopes: $($grant.scope)"

# ---- 5. summarize --------------------------------------------------------
Write-Section "Done"
Write-Host "App ready for MSAL device-code flow." -ForegroundColor Green
Write-Host ""
Write-Host "Set these env vars for the rest of your session:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  `$env:JOJO_MSAL_CLIENT_ID = '$ClientId'"
Write-Host "  `$env:JOJO_MSAL_TENANT_ID = '$TenantId'"
Write-Host ""
Write-Host "Then seed the token cache once (interactive device-code prompt):" -ForegroundColor Cyan
Write-Host "  jojo-ingest login"
Write-Host ""
Write-Host "After that, scheduled ingests will refresh silently for ~90 days."
Write-Host ""
Write-Host "To make these permanent for your user (so you don't have to re-set"
Write-Host "them each shell), use:" -ForegroundColor Cyan
Write-Host "  [Environment]::SetEnvironmentVariable('JOJO_MSAL_CLIENT_ID', '$ClientId', 'User')"
Write-Host "  [Environment]::SetEnvironmentVariable('JOJO_MSAL_TENANT_ID', '$TenantId', 'User')"
