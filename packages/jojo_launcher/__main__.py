from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn

PORT = 8766


def _is_running() -> bool:
    try:
        s = socket.create_connection(("127.0.0.1", PORT), timeout=0.5)
        s.close()
        return True
    except OSError:
        return False


def _wait_ready(timeout: float = 30.0) -> bool:
    import urllib.request

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def main() -> None:
    print("=" * 60)
    print("  JoJo Bot is starting.")
    print("  A browser tab will open shortly.")
    print("  KEEP THIS WINDOW OPEN — closing it stops JoJo Bot.")
    print("=" * 60)

    if _is_running():
        print("\nJoJo Bot is already running. Opening your browser...")
        webbrowser.open(f"http://127.0.0.1:{PORT}")
        return

    # In frozen mode, point wiki_root at the sibling ask_jojo_wiki/ directory
    # so the /wiki-outputs mount in main.py resolves correctly.
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).parent  # dist/JojoBot/
        sibling_wiki = exe_dir.parent / "ask_jojo_wiki"
        if sibling_wiki.exists():
            os.environ.setdefault("JOJO_WIKI_ROOT", str(sibling_wiki))
        sibling_raw = exe_dir.parent / "ask_jojo_raw"
        if sibling_raw.exists():
            os.environ.setdefault("JOJO_RAW_ROOT", str(sibling_raw))

    # Import here so PyInstaller can find the app object in the bundle
    from backend.main import app  # noqa: PLC0415

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="info"))

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    print("\nWaiting for server to start...")
    if _wait_ready():
        print(f"Server ready. Opening http://127.0.0.1:{PORT} ...")
        webbrowser.open(f"http://127.0.0.1:{PORT}")
    else:
        print("[warn] Server did not respond in 30s. Check for errors above.")

    print("\nPress Ctrl+C to stop JoJo Bot.\n")
    try:
        thread.join()
    except KeyboardInterrupt:
        server.should_exit = True
        thread.join()

    print("\nJoJo Bot stopped.")


if __name__ == "__main__":
    main()
