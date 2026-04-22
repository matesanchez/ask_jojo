"""`.jojoignore` parser — gitignore-style filtering for ingest and compile.

Per PLAN.md §6 Phase 1, `.jojoignore` excludes noisy folders (build artifacts,
drafts, scratch) from both the ingest walk and later absorb passes. The syntax
mirrors gitignore: one pattern per line, `#` comments, `!` negation, `/`
prefix for rooted matches, trailing `/` for directory-only.

We deliberately reimplement the subset we need rather than pulling in
`pathspec` — the rules are ~50 lines and avoiding the dep keeps ingest lean.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class _Rule:
    pattern: str
    negate: bool
    directory_only: bool
    rooted: bool


class JojoIgnore:
    """Evaluate whether a path should be ignored by ingest.

    Usage:
        ignore = JojoIgnore.from_file(root / ".jojoignore")
        if ignore.match(path, is_dir=False):
            continue
    """

    _DEFAULT_PATTERNS: tuple[str, ...] = (
        # Office lock files — never useful, always noise.
        "~$*",
        "*.tmp",
        # Common build/cache directories.
        ".git/",
        ".venv/",
        "__pycache__/",
        "node_modules/",
        ".next/",
        "dist/",
        "build/",
        # OS junk.
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
        # Ingest-internal files — never ingest ourselves.
        ".jojoignore",
    )

    def __init__(self, rules: list[_Rule] | None = None) -> None:
        self._rules: list[_Rule] = list(rules or [])

    @classmethod
    def from_file(cls, path: Path | str) -> JojoIgnore:
        rules = [_compile_rule(p) for p in cls._DEFAULT_PATTERNS]
        p = Path(path)
        if p.exists():
            for raw in p.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                rules.append(_compile_rule(line))
        return cls(rules)

    @classmethod
    def from_patterns(cls, patterns: list[str]) -> JojoIgnore:
        rules = [_compile_rule(p) for p in cls._DEFAULT_PATTERNS]
        rules.extend(_compile_rule(p) for p in patterns)
        return cls(rules)

    def match(self, path: str | Path, *, is_dir: bool = False) -> bool:
        """Return True if `path` should be ignored.

        `path` is a POSIX-style relative path against the ignore-file's root.
        Directory rules (trailing `/`) match when the path itself is a
        directory *or* when any of its ancestors match — gitignore semantics:
        ignoring `drafts/` also ignores `drafts/x.md`.
        """
        rel = Path(path).as_posix()
        if rel.startswith("./"):
            rel = rel[2:]
        rel = rel.lstrip("/")
        segments = rel.split("/")
        matched = False
        for rule in self._rules:
            if rule.directory_only:
                if is_dir and _rule_matches(rule, rel):
                    matched = not rule.negate
                    continue
                # Ancestor match — walk the parent chain.
                for i in range(len(segments) - 1):
                    ancestor = "/".join(segments[: i + 1])
                    if _rule_matches(rule, ancestor):
                        matched = not rule.negate
                        break
            else:
                if _rule_matches(rule, rel):
                    matched = not rule.negate
        return matched


def _compile_rule(raw: str) -> _Rule:
    line = raw
    negate = False
    if line.startswith("!"):
        negate = True
        line = line[1:]
    directory_only = line.endswith("/")
    if directory_only:
        line = line.rstrip("/")
    rooted = line.startswith("/")
    if rooted:
        line = line.lstrip("/")
    return _Rule(pattern=line, negate=negate, directory_only=directory_only, rooted=rooted)


def _rule_matches(rule: _Rule, rel_path: str) -> bool:
    segments = rel_path.split("/")
    if rule.rooted:
        # Only match from the root downward.
        return fnmatch.fnmatchcase(rel_path, rule.pattern) or _prefix_match(rule.pattern, rel_path)
    # Unrooted: match any path segment or the whole relative path.
    if fnmatch.fnmatchcase(rel_path, rule.pattern):
        return True
    return any(fnmatch.fnmatchcase(seg, rule.pattern) for seg in segments)


def _prefix_match(pattern: str, rel_path: str) -> bool:
    # For rooted dir patterns like `drafts/` applied to `drafts/x/y.md`.
    if "/" not in pattern:
        return rel_path.split("/", 1)[0] == pattern
    return rel_path == pattern or rel_path.startswith(pattern + "/")
