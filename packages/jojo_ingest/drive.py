"""Local-path / SMB drive connector.

Walks a root directory and emits one `SourceEntry` per readable file. The
`.jojoignore` at the root (if any) filters the walk -- default ignores cover
Office lock files, OS junk, and common build directories.

SMB paths work too: pass `\\\\server\\share\\folder` (Windows) or a mounted
`/mnt/smb/share` (Linux/macOS). The connector treats them as ordinary
filesystem paths; the only quirk is that `os.stat` can be slow over SMB, so
`--incremental --since <iso>` is strongly recommended for scheduled runs.

Hang resilience (FU-9): every blocking filesystem call -- `scandir`,
`stat`, and the per-file `convert` hand-off -- is routed through
`jojo_ingest._watchdog.run_with_timeout`. If a call doesn't return within
its timeout, the walker logs the path and moves on. Without this guard a
single torn-down SMB session can deadlock the whole run (the symptom from
the April 22 soak: 12h wall-clock, zero additions, zero errors).

Listing strategy: directory entries come from `os.scandir`, which on
Windows fills DirEntry.is_dir() and DirEntry.stat() from the same
FindFirstFile/FindNextFile call that produced the listing -- the walker
pays one SMB round-trip per directory instead of one per directory plus
N per file. On a deeply-nested share this is the difference between a
walk that finishes in minutes and one that runs into the next day.

Files whose extension has a dedicated converter (docx/xlsx/pptx/pdf) round-
trip through that converter. Anything else that decodes as text falls back
to the text converter. Binary files with unknown extensions are skipped and
logged. Files larger than `max_size_mb` (default 50 MB) are skipped before
the converter ever opens them -- this matches the SharePoint connector's
default and keeps a random 4 GB CAD file on P:\\ from exploding the walker.

`include_extensions` narrows the walker to a whitelist (lowercase, no dot)
when set. Useful on huge shares like the public P:\\ drive where the bulk
is raw instrument output and only docx/pptx/pdf are worth ingesting --
passing `include_extensions={"docx","pptx","pdf"}` skips the rest at the
walker (before stat, before convert) so the run never touches them. Default
of None preserves the original behavior (any supported extension).

`progress_interval_s` controls a periodic heartbeat printed to stderr
naming the directory the walker is currently in plus the running yield
count. Default 60s. The 50 TB P:\\ walk takes hours; without this an
operator tailing the log can't tell whether the run is making progress
or hung on a single subtree. Set <= 0 to disable.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from collections.abc import Iterable, Iterator
from datetime import datetime, timezone
from pathlib import Path

from jojo_connectors_common import (
    Connector,
    IngestError,
    JojoIgnore,
    SourceEntry,
)
from jojo_ingest._watchdog import WatchdogTimeout, run_with_timeout
from jojo_ingest.converters import ConverterNotFound, convert, is_supported

log = logging.getLogger(__name__)

# Defaults picked to match operational experience:
#   - 30s is longer than any healthy SMB scandir in our testing (median < 1s,
#     p99 < 5s) but short enough that a stuck subtree doesn't eat hours.
#   - 10s covers a cold-cache stat over SMB with plenty of slack; longer than
#     that and something is wrong.
#   - 120s for convert covers pathological xlsx/pdf files; beyond that
#     something is hung (fitz on a corrupt PDF, openpyxl on shared-string
#     weirdness) and we'd rather skip than wait.
_DEFAULT_LISTDIR_TIMEOUT_S = 30.0
_DEFAULT_STAT_TIMEOUT_S = 10.0
_DEFAULT_CONVERT_TIMEOUT_S = 120.0

# Heartbeat cadence for the walker. 60s is slow enough that the log file
# doesn't drown in updates on a fast local walk, fast enough that an
# operator tailing the wrapper log on a multi-day P:\ run can tell which
# subtree we're chewing on. Set <= 0 to disable.
_DEFAULT_PROGRESS_INTERVAL_S = 60.0


def _scandir_sorted(directory: str) -> list[os.DirEntry]:
    """List `directory` via `os.scandir`, drained and sorted by name.

    The DirEntry list is materialized inside the watchdog thread's
    `with os.scandir(...)` block so the OS handle is closed before we
    return — leaving it open across a thread boundary risks a leak if
    the watchdog abandons the thread. Sorting by name gives the walker
    deterministic output (mirroring the previous `Path.iterdir()` +
    `sorted(...)` behavior so existing snapshots keep their order).

    `directory` is a `str` rather than a `Path` because os.scandir on
    Windows is meaningfully faster on str paths than on Path objects
    (Path adds a `__fspath__` round-trip per entry); the caller passes
    `str(path)` once, the walk does its work, and the cost is paid once.
    """
    with os.scandir(directory) as it:
        return sorted(it, key=lambda e: e.name)


class DriveConnector(Connector):
    source_type = "drive"

    # Subclasses may set this to a tuple of gitignore-style patterns that
    # ship with the connector itself, layered on top of the source root's
    # `.jojoignore`. The use case is shares the operator can't write to
    # (e.g. the Nurix P:\ public drive — see PublicDriveConnector) where
    # noisy subtrees still need pruning. Empty by default so the base
    # connector doesn't impose policy on plain local-folder walks.
    _BUILTIN_IGNORE_PATTERNS: tuple[str, ...] = ()

    def __init__(
        self,
        root: Path | str,
        *,
        access_level: str = "all_fte",
        ignore: JojoIgnore | None = None,
        max_size_mb: int = 50,
        include_extensions: Iterable[str] | None = None,
        extra_ignore_patterns: Iterable[str] | None = None,
        listdir_timeout_s: float = _DEFAULT_LISTDIR_TIMEOUT_S,
        stat_timeout_s: float = _DEFAULT_STAT_TIMEOUT_S,
        convert_timeout_s: float = _DEFAULT_CONVERT_TIMEOUT_S,
        progress_interval_s: float = _DEFAULT_PROGRESS_INTERVAL_S,
    ) -> None:
        self.root = Path(root).resolve()
        if not self.root.exists():
            raise IngestError(f"drive root does not exist: {self.root}")
        self.access_level = access_level
        # Resolution order for the ignore set:
        #   1. Caller-supplied `ignore` (full override; tests use this)
        #   2. Source root's .jojoignore + class _BUILTIN_IGNORE_PATTERNS
        #      + caller-supplied extra_ignore_patterns
        # The class builtins go BEFORE the operator extras so an operator
        # can negate a builtin pattern with a `!` rule if they ever need
        # to (gitignore semantics: later rules override earlier ones).
        if ignore is not None:
            self.ignore = ignore
        else:
            base = JojoIgnore.from_file(self.root / ".jojoignore")
            extras: list[str] = list(self._BUILTIN_IGNORE_PATTERNS)
            if extra_ignore_patterns:
                extras.extend(extra_ignore_patterns)
            self.ignore = base.with_extra(extras) if extras else base
        self.max_bytes = max_size_mb * 1024 * 1024
        # Normalize: lowercase, strip leading dots, drop empties. None means
        # "no allowlist" (current behavior); a frozenset means "only these".
        # Order matters: strip whitespace before the leading dot, else
        # " .pptx" lstrips on the leading space and the dot survives.
        self.include_extensions: frozenset[str] | None = (
            frozenset(
                e.strip().lower().lstrip(".")
                for e in include_extensions
                if e and e.strip()
            )
            if include_extensions is not None
            else None
        )
        self.listdir_timeout_s = listdir_timeout_s
        self.stat_timeout_s = stat_timeout_s
        self.convert_timeout_s = convert_timeout_s
        self.progress_interval_s = progress_interval_s
        # Mutable per-run state. Reset in fetch() so that re-using a connector
        # instance across runs doesn't carry stale counts or timestamps.
        self._last_progress_at: float = 0.0
        self._yielded: int = 0

    def fetch(self, *, since: datetime | None = None) -> Iterable[SourceEntry]:
        # Reset the heartbeat state at the top of each run. Force a progress
        # line on the first directory by leaving _last_progress_at at 0; the
        # gate below treats an unset timestamp as "always emit".
        self._last_progress_at = 0.0
        self._yielded = 0
        yield from self._walk(self.root, since=since)

    def _walk(self, directory: Path, *, since: datetime | None) -> Iterator[SourceEntry]:
        # Heartbeat fires on directory entry rather than per-file: per-file
        # would spam on a fat directory, and the operator just wants to know
        # which subtree we're in. Emitted before scandir() so a hang shows
        # up in the log right next to the directory we got stuck on.
        self._emit_progress(directory)
        # `os.scandir` instead of `Path.iterdir` is the cheap perf win: on
        # Windows (and most POSIX filesystems) the directory listing fills
        # in DirEntry.is_dir() and DirEntry.stat() from the same underlying
        # FindFirstFile/FindNextFile (or readdir+inline-stat) sweep, so a
        # later .is_dir() / .stat() call on a DirEntry is satisfied from
        # cache without a second SMB round-trip. The pre-fix walker did
        # 1 listdir + N stat() syscalls per directory; the new walker does
        # 1 scandir + 0 syscalls per directory in the common case. On a
        # 10k-file SMB subtree that's the difference between minutes and
        # seconds. We still route through the watchdog so a torn-down SMB
        # session can't deadlock the walker (FU-9).
        try:
            children = run_with_timeout(
                _scandir_sorted,
                str(directory),
                timeout_s=self.listdir_timeout_s,
                label=f"scandir({directory})",
            )
        except PermissionError:
            log.warning("permission denied, skipping: %s", directory)
            return
        except WatchdogTimeout as exc:
            # This is the FU-9 case: SMB session torn down, scandir never
            # returns. Daemon thread is abandoned; the walker moves on.
            log.warning("listdir timed out on %s, skipping subtree: %s", directory, exc)
            return
        except OSError as exc:
            # Broader I/O failure at the directory level -- most commonly a
            # transient SMB blip on the public P: drive. Typical errnos:
            #   WinError 59 ("unexpected network error")
            #   WinError 64 ("network name no longer available")
            #   WinError 67 ("network name cannot be found")
            #   WinError 1231 ("network location cannot be reached")
            # Log loudly but keep walking -- one bad subtree is never worth
            # losing the entire run's worth of already-yielded entries.
            log.warning("I/O error listing %s, skipping subtree: %s", directory, exc)
            return
        for entry in children:
            entry_path = Path(entry.path)
            rel = entry_path.relative_to(self.root).as_posix()
            # is_dir / is_file from a DirEntry are answered from the
            # listing's cached stat info on Windows, so these don't make
            # extra syscalls in the common case. follow_symlinks=False is
            # deliberate: a circular symlink on a share would otherwise
            # make the walk recurse forever.
            try:
                is_directory = entry.is_dir(follow_symlinks=False)
            except OSError as exc:
                # Stat failed for this one entry (rare; happens if a file is
                # deleted between scandir and is_dir, or on a flaky SMB session).
                # Skip the entry but don't bail on the directory.
                log.warning("is_dir failed on %s, skipping: %s", entry.path, exc)
                continue
            if is_directory:
                if self.ignore.match(rel, is_dir=True):
                    # Visible debug-level so an operator chasing "why is the
                    # walker fast / what got skipped?" can grep the wrapper
                    # log. Kept at debug to avoid drowning the normal log.
                    log.debug("ignore match (dir), pruning subtree: %s", rel)
                    continue
                yield from self._walk(entry_path, since=since)
                continue
            if self.ignore.match(rel, is_dir=False):
                continue
            if not is_supported(entry_path):
                log.info("unsupported extension, skipping: %s", rel)
                continue
            if self.include_extensions is not None:
                # Empty extension ("" — files with no suffix) is intentionally
                # excluded when an allowlist is set: the operator was explicit,
                # so don't let unmarked text files sneak in.
                ext = entry_path.suffix.lower().lstrip(".")
                if ext not in self.include_extensions:
                    log.debug("not in include_extensions, skipping: %s", rel)
                    continue
            stat = self._safe_stat_dirent(entry)
            if stat is None:
                continue
            if stat.st_size > self.max_bytes:
                log.info(
                    "skipping %s: %d bytes > max_size %d",
                    rel, stat.st_size, self.max_bytes,
                )
                continue
            if since is not None:
                mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                if mtime < since:
                    continue
            se = self._build_entry(entry_path, rel, stat=stat)
            if se is not None:
                self._yielded += 1
                yield se

    def _emit_progress(self, current: Path) -> None:
        """Print a one-line walker heartbeat to stderr, gated by interval.

        Stderr (not logging) so the wrapper's `2>&1` tee picks it up
        regardless of log level, and so it stays visible even if a future
        change quietens this module's logger. `flush=True` because the
        wrapper writes the log file via Out-File which buffers by default.
        """
        if self.progress_interval_s <= 0:
            return
        now = time.monotonic()
        if self._last_progress_at and (now - self._last_progress_at) < self.progress_interval_s:
            return
        self._last_progress_at = now
        # Relative path is friendlier than the full SMB path; "." for the
        # root keeps the message readable on the very first emit.
        try:
            rel = current.relative_to(self.root).as_posix() or "."
        except ValueError:
            # Walker should never leave self.root, but if it does, fall back
            # to the absolute path rather than crashing the heartbeat.
            rel = str(current)
        print(
            f"[progress] {self.source_type}: walking {rel} "
            f"(yielded {self._yielded} so far)",
            file=sys.stderr,
            flush=True,
        )

    def _safe_stat(self, path: Path):
        """Stat a single path with a watchdog timeout. Returns None on failure.

        Over SMB an `os.stat` on a handle whose session was torn down can
        block indefinitely. We route every stat through the watchdog so
        the walker never gets stuck on one file.

        Retained for the `_build_entry` fallback path where we only have
        a Path and no DirEntry cache to consult; the hot walker loop uses
        `_safe_stat_dirent` against the scandir cache instead.
        """
        try:
            return run_with_timeout(
                path.stat,
                timeout_s=self.stat_timeout_s,
                label=f"stat({path})",
            )
        except WatchdogTimeout as exc:
            log.warning("stat timed out on %s, skipping: %s", path, exc)
            return None
        except OSError as exc:
            log.warning("stat failed on %s, skipping: %s", path, exc)
            return None

    def _safe_stat_dirent(self, entry: os.DirEntry):
        """Stat a DirEntry from `os.scandir`, watchdog-wrapped.

        On Windows DirEntry.stat() is filled in from the original
        FindFirstFile/FindNextFile call, so the call is essentially free
        (no second roundtrip). On POSIX it's a real `lstat` syscall on
        first access, then cached. We still route through the watchdog
        because a degraded SMB session can stall a stat() the first time
        the cache is cold.
        """
        try:
            return run_with_timeout(
                lambda: entry.stat(follow_symlinks=False),
                timeout_s=self.stat_timeout_s,
                label=f"stat({entry.path})",
            )
        except WatchdogTimeout as exc:
            log.warning("stat timed out on %s, skipping: %s", entry.path, exc)
            return None
        except OSError as exc:
            log.warning("stat failed on %s, skipping: %s", entry.path, exc)
            return None

    def _build_entry(self, path: Path, rel: str, *, stat=None) -> SourceEntry | None:
        try:
            body = run_with_timeout(
                convert,
                path,
                timeout_s=self.convert_timeout_s,
                label=f"convert({rel})",
            )
        except ConverterNotFound:
            return None
        except WatchdogTimeout as exc:
            # A converter that never returns is either pegged on a
            # corrupt file or stuck inside a C extension we can't
            # interrupt. Skip and move on.
            log.warning("convert timed out on %s, skipping: %s", path, exc)
            return None
        except Exception as exc:  # noqa: BLE001 -- one bad file must not stop the walk
            log.warning("failed to convert %s: %s", path, exc)
            return None
        if stat is None:
            stat = self._safe_stat(path)
        if stat is not None:
            modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            created = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
        else:
            modified = None
            created = None
        return SourceEntry(
            source_type=self.source_type,
            source_id=rel,
            source_url=path.as_uri(),
            title=path.stem,
            content=body,
            access_level=self.access_level,
            author="",
            created=created,
            modified=modified,
            tags=[],
        )
