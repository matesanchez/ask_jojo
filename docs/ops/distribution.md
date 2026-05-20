# JoJo Bot v2.0 -- Department Workstation Install Guide

This guide is written for department staff, not developers. You do not need
PowerShell or Python knowledge to install JoJo Bot.

---

## Prerequisites

1. **Windows 10 or 11** (64-bit). JoJo Bot runs as a background Windows Service.
2. **Administrator access on the workstation** for the install step only. Day-to-day
   use does not require admin. Ask your IT contact or Mateo de los Rios if you need
   elevation.

That is all. The zip file contains everything else -- no internet access is required
during installation.

---

## Install

1. **Download the zip file** from the link provided by Mateo de los Rios (typically
   on the Nurix SharePoint site or shared via email). The file is named something like
   `JojoBot-v2.0.0.zip`.

2. **Extract the zip.** Right-click the file and select "Extract All". Extract to a
   folder you choose, for example `C:\JojoBot\`. You should see these files after
   extracting:

   ```
   C:\JojoBot\JojoBot-v2.0.0\
     Install-JojoBot.ps1
     Uninstall-JojoBot.ps1
     Install-Service.ps1
     python\
     frontend\
     README.txt
   ```

3. **Run the installer.** Right-click `Install-JojoBot.ps1` and select
   **"Run with PowerShell"**. If Windows asks whether to allow the script,
   click **"Open"** or **"Run anyway"**.

   - A black window will open and show progress messages.
   - When prompted for administrator access (UAC), click **Yes**.
   - The installer registers the JoJo Bot Windows Service and starts it.

4. **Your browser opens automatically** to `http://localhost:8765/welcome`.
   If it does not open after 10 seconds, type that address into your browser manually.

---

## First-time setup

After the installer finishes:

1. The browser shows the JoJo Bot welcome page at `http://localhost:8765/welcome`.

2. Click **Settings** in the navigation bar.

3. Paste your **Anthropic API key** into the "API Key" field and click Save.
   - If you do not have an API key, contact Mateo de los Rios.

4. Confirm the connector paths shown on the Settings page:
   - **OneDrive folder** -- should match your synced OneDrive location
     (e.g., `C:\Users\you\OneDrive - Nurix Therapeutics`).
   - **Public Drive (P:\)** -- should show `P:\` if the drive is mapped.

5. Click **Run Ingest** on the Ingest tab to build the knowledge base from your
   connected drives. The first ingest can take several hours for a large drive.

Once ingest completes, all five tabs are active: Ask, Wiki, Raw, Viz, Settings.

---

## Uninstall

1. Navigate to the folder where you extracted the zip
   (e.g., `C:\JojoBot\JojoBot-v2.0.0\`).

2. Right-click `Uninstall-JojoBot.ps1` and select **"Run with PowerShell"**.

3. The script asks whether to delete your config file and data directories.
   Press **Enter** to keep them (recommended if you plan to re-install later),
   or type `y` and press Enter to delete them.

4. The JoJo Bot Windows Service is removed. The background process stops.

To do a complete wipe (no traces left on the machine), run:
```
Uninstall-JojoBot.ps1 -Purge -Force
```
from a PowerShell window with administrator privileges.

---

## Troubleshooting

### The browser does not open after install

The service may need a few extra seconds to start. Wait 15 seconds, then
navigate to `http://localhost:8765/` manually. If you see a connection error,
the service is not running. Open PowerShell and run:

```powershell
Start-Service JojoBot
```

If that command fails with "Access Denied", run PowerShell as Administrator.

---

### "NSSM not found" message during install

NSSM is the service manager that captures JoJo Bot logs. If the installer
reports it is not found, it will fall back to the built-in `sc.exe` service
manager instead. JoJo Bot will still work; you just lose automatic log capture.
The service will still restart on failure.

To add NSSM later: download `nssm-2.24.zip` from nssm.cc, extract `nssm.exe`
beside `Install-Service.ps1`, and run:

```powershell
Install-Service.ps1 -AppPath .\python\jojo-server.exe -Force
```

---

### API key invalid error in the Ask tab

The Anthropic API key was not saved correctly. Go to **Settings**, re-paste
your API key, and click Save. The key starts with `sk-ant-`. If you do not
have a key, contact Mateo de los Rios.

---

### Service stops unexpectedly / crashes after a few hours

Check the service log for errors:

```powershell
Get-Content "$env:ProgramData\JojoBot\logs\stderr.log" -Tail 100
```

Common causes:
- OneDrive token expired: re-authenticate via the Settings tab.
- Out of disk space on the drive where `ask_jojo_raw\` is stored.
- Python import error after an update: re-run the installer.

The service is configured to restart automatically (10 s after first failure,
30 s after subsequent failures). Brief blips are self-healing.

---

### LAN access for a shared screen (projector workstation)

By default JoJo Bot only accepts connections from the local machine
(`localhost`). To allow other computers on the department LAN to connect, run
the installer with an extra flag:

```powershell
Install-JojoBot.ps1 -BindAddress 0.0.0.0
```

**Warning:** this exposes the JoJo Bot UI to everyone on the local network
segment. Only do this on a physically-secured department workstation behind
the Nurix firewall. The welcome page will display a warning when LAN access
is enabled.

---

## Operations reference (for the person managing the install)

### File locations

| Item | Path |
|------|------|
| Config (API key, paths) | `%APPDATA%\JojoBot\config.json` |
| Service logs | `%ProgramData%\JojoBot\logs\` |
| Wiki pages | Configured in Settings (default: `ask_jojo_wiki\`) |
| Raw ingest files | Configured in Settings (default: `ask_jojo_raw\`) |

### Service management

```powershell
Get-Service JojoBot                          # check status
Start-Service JojoBot                        # start
Stop-Service JojoBot                         # stop
Restart-Service JojoBot                      # restart
Get-Content "$env:ProgramData\JojoBot\logs\stderr.log" -Tail 50  # tail logs
```

### Upgrading

1. Stop the service: `Stop-Service JojoBot`
2. Extract the new zip to a new folder (e.g., `C:\JojoBot\JojoBot-v2.0.1\`).
3. Run `Install-JojoBot.ps1 -Force` from the new folder.
   Config and data directories are untouched by default.
4. Verify `http://localhost:8765/` is working.
5. Delete the old folder when satisfied.

### Building a new release (developer reference)

From the `ask_jojo` repo root on a dev machine with PyInstaller and Node.js:

```powershell
.\ops\installer\Build-JojoBotRelease.ps1 -Version 2.0.1
```

The zip lands at `dist\JojoBot-v2.0.1.zip`. Dry-run validation:

```powershell
.\ops\installer\Build-JojoBotRelease.ps1 -DryRun
```

Frontend static export compatibility note: the current `src\frontend\next.config.js`
uses `rewrites()`, which is incompatible with Next.js static export. Until the
frontend is updated to use `output: 'export'`, the Build script writes a note to
`dist\frontend-build-note.txt` and the zip ships a placeholder `frontend\`
directory. The API at `http://localhost:8765/api/` and the Swagger docs at
`http://localhost:8765/docs` are fully functional; only the React UI is absent.
Track this in the frontend agent backlog.

### Security

The config file is DPAPI-encrypted using the machine key. Any user with local
administrator access to the workstation can decrypt it. This is acceptable for a
shared department workstation (see ADR 0013). Do not store credentials beyond
what JoJo Bot requires.

The service binds to `127.0.0.1:8765` by default. No ports are exposed externally
unless `-BindAddress 0.0.0.0` is explicitly passed to the installer.
