"""Thread-based timeout watchdog for blocking syscalls and converters.

Why this exists: FU-9 — `DriveConnector._walk` can block forever on SMB
syscalls (`os.scandir`, `os.stat`) when the network link goes through a
selective-suspend NIC and the SMB session is silently torn down. The
syscall never returns; the regular `OSError` catch does nothing because
there's no error to catch. Converters like `fitz.open` on a pathological
PDF or `openpyxl.load_workbook` on a broken xlsx exhibit the same
symptom — they just don't return.

Cross-platform constraint: `signal.SIGALRM` doesn't exist on Windows, so
we can't use signal-based timeouts. Python has no portable way to
forcibly kill a thread either. So we do the next-best thing: run the
blocking call in a daemon thread and abandon it if it hasn't finished in
time. The walker keeps moving; the worker thread may leak, but because
it's a daemon it can't keep the process alive past shutdown.

This is deliberately tiny — no executor pool, no cancellation machinery.
If the blocked thread ever returns, its result is discarded. If it never
returns, the daemon flag keeps it from blocking interpreter exit.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class WatchdogTimeout(TimeoutError):
    """Raised when `run_with_timeout` exceeds its deadline.

    Subclass of the builtin `TimeoutError` so callers can either catch it
    specifically or catch any timeout the same way.
    """


def run_with_timeout(
    func: Callable[..., T],
    *args: Any,
    timeout_s: float,
    label: str = "",
    **kwargs: Any,
) -> T:
    """Run `func(*args, **kwargs)` in a daemon thread and wait up to `timeout_s`.

    Returns the function's result on success. On timeout raises
    `WatchdogTimeout`. If the function itself raises, that exception is
    re-raised on the calling thread unchanged.

    `label` is only used in the timeout error message so callers can tell
    which walk/convert was stuck.
    """
    if timeout_s <= 0:
        raise ValueError(f"timeout_s must be positive, got {timeout_s}")

    slot: dict[str, Any] = {}

    def _target() -> None:
        try:
            slot["result"] = func(*args, **kwargs)
        except BaseException as exc:  # noqa: BLE001 — propagate, don't swallow
            slot["exc"] = exc

    t = threading.Thread(
        target=_target,
        name=f"jojo-watchdog({label or func.__name__})",
        daemon=True,
    )
    t.start()
    t.join(timeout_s)
    if t.is_alive():
        raise WatchdogTimeout(
            f"{label or func.__name__} exceeded {timeout_s:.1f}s "
            "(thread abandoned; walker will continue)"
        )
    if "exc" in slot:
        raise slot["exc"]
    return slot["result"]
