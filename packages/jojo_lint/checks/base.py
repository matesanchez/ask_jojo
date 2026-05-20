"""Base types shared across all lint checks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CheckResult:
    """Result from a single lint check.

    Attributes:
        check_name: identifier matching the key in ``NIGHTLY_CHECKS`` or
            ``WEEKLY_CHECKS``.
        status: ``"pass"`` | ``"warn"`` | ``"fail"`` | ``"api_key_required"``.
        findings: list of finding dicts, each with at minimum:
            ``{slug, message, severity}`` where severity is one of
            ``"error"``, ``"warn"``, ``"info"``.
        run_at: ISO 8601 UTC datetime string.
        duration_ms: wall-clock milliseconds the check took.
    """

    check_name: str
    status: str
    findings: list[dict]  # type: ignore[type-arg]
    run_at: str
    duration_ms: int = 0

    def to_dict(self) -> dict:  # type: ignore[type-arg]
        """Return a JSON-serializable representation."""
        return {
            "check_name": self.check_name,
            "status": self.status,
            "findings": self.findings,
            "run_at": self.run_at,
            "duration_ms": self.duration_ms,
        }
