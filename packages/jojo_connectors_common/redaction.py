"""Pre-LLM PII/PHI redaction pass.

Per PLAN.md §6 Phase 1 invariants: every raw file runs through a regex
redaction pass at ingest time. The goal is not to be a perfect PII classifier
(the LLM pass in Phase 2 does the deep cleanup) — it is to get any obvious
patterns replaced before content touches disk or the Claude API.

Add patterns as Legal/Compliance surface them. Err toward over-redaction: a
missed pattern is worse than a false positive.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from re import Pattern

# (field name, compiled pattern, placeholder)
_PATTERNS: list[tuple[str, Pattern[str], str]] = [
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED:ssn]"),
    (
        "credit_card",
        re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
        "[REDACTED:credit_card]",
    ),
    (
        "email",
        re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
        "[REDACTED:email]",
    ),
    (
        "phone_us",
        # Negative lookbehind/ahead on digits instead of \b — \b fails between
        # whitespace and "(" since both are non-word characters.
        re.compile(r"(?<!\d)(?:\+?1[ .\-]?)?(?:\(\d{3}\)|\d{3})[ .\-]?\d{3}[ .\-]?\d{4}(?!\d)"),
        "[REDACTED:phone]",
    ),
    (
        "patient_id",
        # Pattern: two letters + 6-10 digits OR "PT" / "MRN" prefix + digits
        re.compile(r"\b(?:PT|MRN|PAT)[-:]?\d{5,10}\b", re.IGNORECASE),
        "[REDACTED:patient_id]",
    ),
    (
        "dob",
        # Common date-of-birth patterns: 01/23/1980, 1980-01-23, 23 Jan 1980
        re.compile(
            r"\b(?:DOB[:\s]+)?(?:"
            r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
            r"|\d{4}[/-]\d{1,2}[/-]\d{1,2}"
            r")\b",
            re.IGNORECASE,
        ),
        "[REDACTED:dob]",
    ),
]

# Whitelist of emails we explicitly keep (e.g. corporate auto-generated).
# Add carefully — anything matching this skips redaction.
_EMAIL_WHITELIST = re.compile(
    r"\b(?:noreply|no-reply|donotreply|do-not-reply|notifications?)"
    r"@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)


@dataclass(slots=True)
class RedactionResult:
    content: str
    redacted_fields: list[str] = field(default_factory=list)
    match_counts: dict[str, int] = field(default_factory=dict)


def redact_pii(text: str) -> RedactionResult:
    """Run the regex redaction pass over `text`.

    Returns the redacted content plus the list of field-types that matched.
    The manifest records this list so downstream consumers can surface what
    was scrubbed without re-scanning the file.

    DoB and email patterns are the noisiest — if you see them swallowing
    legitimate content (conference dates, mailing lists), tune the patterns
    above rather than disabling the pass.
    """
    fields_hit: dict[str, int] = {}
    working = text

    # Preserve whitelisted emails before we scan.
    whitelist_sentinel = "\x00WHITELIST\x00"
    replaced_whitelist: list[str] = []

    def _stash_whitelisted(m: re.Match[str]) -> str:
        replaced_whitelist.append(m.group(0))
        return f"{whitelist_sentinel}{len(replaced_whitelist) - 1}{whitelist_sentinel}"

    working = _EMAIL_WHITELIST.sub(_stash_whitelisted, working)

    for name, pattern, placeholder in _PATTERNS:
        new_working, count = pattern.subn(placeholder, working)
        if count:
            fields_hit[name] = fields_hit.get(name, 0) + count
        working = new_working

    # Restore whitelisted emails.
    def _restore(m: re.Match[str]) -> str:
        idx = int(m.group(1))
        return replaced_whitelist[idx]

    working = re.sub(
        f"{whitelist_sentinel}(\\d+){whitelist_sentinel}",
        _restore,
        working,
    )

    return RedactionResult(
        content=working,
        redacted_fields=sorted(fields_hit.keys()),
        match_counts=fields_hit,
    )
