"""JoJo Bot desktop launcher.

Starts the FastAPI/uvicorn server on a free port, then opens the UI in a
native Qt window (PySide6 QWebEngineView) so the app feels like a real
desktop application rather than a browser tab.

Log file: %LOCALAPPDATA%\\JojoBot\\launcher.log
"""
from __future__ import annotations

import logging
import multiprocessing
import os
import socket
import sys
import threading
import time
from pathlib import Path

# ── Logging ────────────────────────────────────────────────────────────────────
_log_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "JojoBot"
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / "launcher.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(_log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("jojo_launcher")

_PREFERRED_PORT = 8766


def _find_free_port(preferred: int = _PREFERRED_PORT) -> int:
    """Return `preferred` if nothing is listening there, else any free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", preferred)) != 0:
            return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_ready(port: int, timeout: float = 45.0) -> bool:
    import urllib.request

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1)
            return True
        except Exception:
            time.sleep(0.4)
    return False


def _setup_data_paths() -> None:
    """In frozen mode, point env vars at the wiki/ and raw/ dirs next to the exe."""
    if not getattr(sys, "frozen", False):
        return
    exe_dir = Path(sys.executable).parent  # dist/JojoBot/
    for env_key, folder in [("JOJO_WIKI_ROOT", "wiki"), ("JOJO_RAW_ROOT", "raw")]:
        candidate = exe_dir / folder
        if candidate.exists():
            os.environ.setdefault(env_key, str(candidate))
            log.info("%s → %s", env_key, candidate)


def _run_server(port: int):
    """Start uvicorn in a daemon thread; return (server, thread)."""
    import uvicorn
    from backend.main import app  # noqa: PLC0415

    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info")
    )
    thread = threading.Thread(target=server.run, daemon=True, name="uvicorn")
    thread.start()
    return server, thread


def _open_window(url: str) -> None:
    """Block until the Qt window closes."""
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QIcon
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWidgets import QApplication

    qt_app = QApplication.instance() or QApplication(sys.argv)

    # Application-level icon (shown in taskbar + alt-tab)
    if getattr(sys, "frozen", False):
        ico = Path(sys.executable).parent / "_internal" / "jojo.ico"
    else:
        ico = Path(__file__).parent.parent.parent / "src" / "frontend" / "public" / "jojo.ico"
    if ico.exists():
        qt_app.setWindowIcon(QIcon(str(ico)))

    view = QWebEngineView()
    view.setWindowTitle("JoJo Bot")
    view.resize(1440, 900)
    view.setMinimumSize(960, 600)
    view.load(QUrl(url))
    view.show()
    qt_app.exec()


def main() -> None:
    # PyInstaller multiprocessing safety — must be the very first call.
    multiprocessing.freeze_support()

    log.info(
        "JoJo Bot starting (frozen=%s, python=%s)",
        getattr(sys, "frozen", False),
        sys.version.split()[0],
    )
    _setup_data_paths()

    port = _find_free_port()
    log.info("Using port %d", port)

    server, thread = _run_server(port)

    log.info("Waiting for server to become ready …")
    if not _wait_ready(port):
        log.error(
            "Server did not respond within 45 s. See full log at %s", _log_file
        )
        return

    log.info("Server ready. Opening window at http://127.0.0.1:%d", port)
    _open_window(f"http://127.0.0.1:{port}")

    log.info("Window closed. Shutting down server …")
    server.should_exit = True
    thread.join(timeout=5)
    log.info("Shutdown complete.")


if __name__ == "__main__":
    main()
