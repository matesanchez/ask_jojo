# JoJo Bot - Build and Install Guide

This guide covers building the JoJo Bot desktop application (`JojoBot.exe`) and
installing it on a new Windows computer. The app is a self-contained desktop
program: once built, the target machine needs no Python, Node, or internet
connection to run it.

There are two deployment shapes. **Most users want the double-click desktop app**
(Section A). The Windows Service install (Section B) is for an always-on shared
workstation. Section C covers installing the finished app on a new computer.

---

## A. Building the double-click desktop app (recommended)

### A.1 Build prerequisites (build machine only)

You build the app once on a developer/build machine; end users never need these.

- Windows 10/11, 64-bit
- Python 3.11 or newer (the reference build used 3.14)
- Node.js 18+ (`npm` on PATH) - needed to compile the web UI
- The three repos cloned as siblings on **local disk** (never inside OneDrive,
  Dropbox, or any synced folder), e.g.:
  `C:\Users\<you>\Claude_Local\jojo_bot_v2.0\{ask_jojo, ask_jojo_wiki, ask_jojo_raw}`

Install the Python build dependencies (run from the `ask_jojo\` folder):

```
pip install -e ".[backend,qa,output,desktop,ingest,lint]"
pip install pyinstaller
```

`[desktop]` pulls in PySide6 (the Qt6 window with the embedded browser engine);
`[backend]`, `[qa]`, `[output]`, `[ingest]`, and `[lint]` cover the FastAPI
server, retrieval, rich-output renderers, file converters, and lint engine that
get bundled into the exe.

### A.2 Build command

From the `ask_jojo\` folder:

```
powershell -ExecutionPolicy Bypass -File ops\installer\Build-JojoExe.ps1 -SkipRaw
```

- **Do NOT pass `-SkipFrontend`.** The committed `src\frontend\out\` is older than
  the current UI source; the build must re-run `npm run build` so the exe ships the
  latest interface. The default (no `-SkipFrontend`) does this for you.
- **`-SkipRaw`** produces a wiki-only build (~tens of MB) suitable for distribution.
  Omit `-SkipRaw` to bundle the full `ask_jojo_raw\` source corpus (10-50+ GB and
  private - only do this for a personal/internal build, never for sharing).
- Optional `-WikiRoot <path>` / `-RawRoot <path>` if the sibling repos live elsewhere.

The script runs four steps: prerequisite check -> `npm run build` -> PyInstaller
(`ops\installer\JojoBot.spec`) -> copy `wiki\` (and `raw\` unless `-SkipRaw`) plus
`README.txt` into the output folder.

### A.3 Build output

```
ask_jojo\dist\JojoBot\
    JojoBot.exe        <- the application
    _internal\         <- bundled Python + Qt runtime (do not move)
    wiki\              <- knowledge base snapshot (Q&A memory)
    raw\               <- source docs (only if you did NOT pass -SkipRaw)
    README.txt
```

To distribute: zip the entire `dist\JojoBot\` folder.

### A.4 Pre-flight checklist

- [ ] On the build machine, in `ask_jojo\`: `python -m PyInstaller --version` works
- [ ] `python -c "from PySide6.QtWebEngineWidgets import QWebEngineView"` prints nothing (no error)
- [ ] `npm --version` works
- [ ] `ask_jojo_wiki\` is a sibling of `ask_jojo\` and holds the latest committed pages
- [ ] Run the build command in A.2 (with `-SkipRaw` for a shareable build)
- [ ] After build: double-click `dist\JojoBot\JojoBot.exe`; the native window opens
- [ ] Smoke test: Wiki tab shows pages; Settings tab accepts an API key; Chat answers a question

---

## B. Windows Service install (always-on shared workstation)

For a workstation that should run JoJo Bot continuously in the background, use the
NSSM-based service installer instead of the desktop app:

```
powershell -ExecutionPolicy Bypass -File ops\installer\Build-JojoBotRelease.ps1
```

This produces a self-contained release `.zip` (frozen Python + Next.js static export +
NSSM service wrapper). On the target machine, run `Install-JojoBot.ps1` from the zip:
it registers the `JojoBot` Windows Service (auto-restart), binds to `localhost:8765`,
and opens the browser to `/welcome`. `Uninstall-JojoBot.ps1` removes it (`-Purge`
also wipes config and data). Configuration is per-user at
`%APPDATA%\JojoBot\config.json` (DPAPI-encrypted secrets). See `docs/ops/distribution.md`.

Most non-developer users do NOT need this - the double-click app in Section A is simpler.

---

## C. Installing the finished app on a new computer

The target machine needs nothing pre-installed - no Python, Node, or internet.

1. Copy the zipped `JojoBot\` folder to the new computer.
2. Unzip it to a location on **local disk** - for example `C:\Tools\JojoBot\` or the
   Desktop. **Do not** unzip into OneDrive, Dropbox, or any synced folder (cloud sync
   corrupts the runtime files and the app database).
3. Open the `JojoBot\` folder and double-click `JojoBot.exe`.
4. After a few seconds the JoJo Bot window opens (a native desktop window - no console,
   no separate browser). First launch may take 10-30 seconds if antivirus inspects the
   new exe; add an exception for `JojoBot.exe` if needed.
5. Open the **Settings** tab and paste an Anthropic API key to enable answer synthesis.
   (Chat works in retrieval-only mode without a key; the Wiki/Raw/Graph tabs work
   regardless.)

To move the app later, move the whole `JojoBot\` folder (keep `wiki\` and `raw\` inside
it). To uninstall, just delete the folder; per-user settings live at
`%APPDATA%\JojoBot\` and logs at `%LOCALAPPDATA%\JojoBot\launcher.log`.

---

## Troubleshooting the build

| Symptom | Fix |
| --- | --- |
| `PyInstaller not installed` | `pip install pyinstaller` in the same environment |
| `PySide6 not installed or QWebEngineView missing` | `pip install -e ".[desktop]"` (or `pip install PySide6`) |
| `npm not found` | Install Node.js 18+ from nodejs.org, reopen the shell |
| UI looks out of date in the built app | You passed `-SkipFrontend`; rebuild without it so `npm run build` runs |
| `ask_jojo_wiki not found` warning | Pass `-WikiRoot <path>` or place `ask_jojo_wiki\` as a sibling of `ask_jojo\` |
| Built exe huge (many GB) | You included `raw\`; rebuild with `-SkipRaw` for distribution |
