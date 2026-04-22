"""Shared connector foundation for jojo_ingest.

Every connector (drive, upload, sharepoint, onedrive, nurixnet) depends on this
package for the base Connector interface, manifest/frontmatter handling,
redaction, and content hashing. Keeping these in a sibling package (rather than
inside jojo_ingest) makes the contract explicit: Phase 2+ packages (compile,
qa, lint) that read raw entries depend on this interface, not on the
connectors themselves.

See ask_jojo/PLAN.md §6 Phase 1 for the governing spec.
"""

__version__ = "0.1.0"

from jojo_connectors_common.base import (
    Connector,
    ConnectorResult,
    IngestError,
    SourceEntry,
)
from jojo_connectors_common.frontmatter import (
    FRONTMATTER_FIELDS,
    AccessLevel,
    SourceType,
    build_frontmatter,
    parse_frontmatter,
    split_frontmatter,
)
from jojo_connectors_common.hashing import canonical_sha256, stable_id
from jojo_connectors_common.ignore import JojoIgnore
from jojo_connectors_common.manifest import Manifest, ManifestEntry
from jojo_connectors_common.redaction import RedactionResult, redact_pii

__all__ = [
    "AccessLevel",
    "Connector",
    "ConnectorResult",
    "FRONTMATTER_FIELDS",
    "IngestError",
    "JojoIgnore",
    "Manifest",
    "ManifestEntry",
    "RedactionResult",
    "SourceEntry",
    "SourceType",
    "build_frontmatter",
    "canonical_sha256",
    "parse_frontmatter",
    "redact_pii",
    "split_frontmatter",
    "stable_id",
]
