# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for JoJo Bot v2.0 desktop application.

Build with:
    cd C:\\Users\\mdelosrios\\Claude_Local\\jojo_bot_v2.0\\ask_jojo
    python -m PyInstaller ops/installer/JojoBot.spec

Output: dist/JojoBot/JojoBot.exe  (+  dist/JojoBot/_internal/)

After the build, Build-JojoExe.ps1 copies:
    ask_jojo_wiki/  →  dist/JojoBot/wiki/
    ask_jojo_raw/   →  dist/JojoBot/raw/
"""
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_all

REPO = Path(SPEC).parent.parent.parent  # ask_jojo/

# ---- Data files (non-Python assets to bundle) --------------------------------
datas = []

# Frontend static export (Next.js out/ → bundled as frontend/out)
frontend_out = REPO / "src" / "frontend" / "out"
if frontend_out.exists():
    datas.append((str(frontend_out), "frontend/out"))

# Jojo packages data files (e.g. JSON defaults, config templates)
for pkg in ["jojo_core", "jojo_qa", "jojo_ingest", "jojo_compile",
            "jojo_graph", "jojo_lint", "jojo_output"]:
    datas += collect_data_files(pkg, include_py_files=False)

# Backend routers (Python source must be in sys.path; --add-data for templates/static)
datas.append((str(REPO / "src" / "backend"), "backend"))

# App icon (placed at _internal/ so the launcher can find it by relative path)
_ico = REPO / "src" / "frontend" / "public" / "jojo.ico"
if _ico.exists():
    datas.append((str(_ico), "."))

# ---- Hidden imports (dynamic imports PyInstaller misses) ---------------------
hiddenimports = []

# Jojo packages (all submodules)
for pkg in ["jojo_core", "jojo_qa", "jojo_ingest", "jojo_compile",
            "jojo_graph", "jojo_lint", "jojo_output", "jojo_launcher"]:
    hiddenimports += collect_submodules(pkg)

# Pydantic v2 (uses importlib-based loading; pydantic_core ships a compiled .pyd)
pydantic_d, pydantic_b, pydantic_h = collect_all("pydantic")
datas += pydantic_d
binaries = list(pydantic_b)
hiddenimports += pydantic_h

# FastAPI / Starlette
hiddenimports += collect_submodules("fastapi")
hiddenimports += collect_submodules("starlette")
hiddenimports += collect_submodules("uvicorn")

# Anthropic SDK (lazy-loaded internally)
hiddenimports += collect_submodules("anthropic")
hiddenimports += ["httpx", "httpcore", "anyio", "sniffio"]

# MSAL (device-code flow)
hiddenimports += collect_submodules("msal")

# Backend routers (transitive dynamic imports inside routers)
hiddenimports += collect_submodules("backend")
hiddenimports += collect_submodules("jojo_connectors_common")

# Other backend deps
hiddenimports += [
    "multipart",
    "python_multipart",
    "email.mime.text",
    "email.mime.multipart",
]

# PySide6 — native Qt window (QWebEngineView).
# PyInstaller 6.x has built-in PySide6 hooks that copy Qt DLLs and
# QtWebEngineProcess.exe automatically; we just need to list the modules.
hiddenimports += [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineCore",
    "PySide6.QtNetwork",
    "PySide6.QtWebChannel",
    "PySide6.QtPositioning",
    "shiboken6",
]

# ---- Excludes (heavy optional tiers not needed in the exe) -------------------
excludes = [
    # Fine-tune tier (ML training; not needed in the daily-use exe)
    "boto3", "botocore", "peft", "transformers", "trl", "datasets",
    "torch", "torchvision",
    # Web scraping tier (cloud-only, needs VPN + running service)
    "playwright", "trafilatura",
    # PDF rendering (weasyprint requires system Cairo/Pango DLLs; exclude to avoid broken PDF)
    "weasyprint", "cairo", "pangocffi",
    # Test frameworks
    "pytest", "pytest_cov", "pytest_httpx",
    # pywebview (not used; PySide6 is the window backend)
    "webview",
]

# ---- Analysis ----------------------------------------------------------------
a = Analysis(
    [str(REPO / "packages" / "jojo_launcher" / "__main__.py")],
    pathex=[
        str(REPO / "packages"),
        str(REPO / "src"),
    ],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="JojoBot",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # No console window — pure GUI app. Logs go to %LOCALAPPDATA%\JojoBot\launcher.log
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(_ico) if _ico.exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="JojoBot",
)
