"""NurixNet connector — stub pending VPN access + Playwright environment.

The production implementation is the most complex connector per PLAN.md §6
Phase 1. Sketch:

  1. **First pass (static HTML)** — `httpx` GET each seed URL; run
     `trafilatura.extract()` then `html2text` on the result. Handles ~80%
     of NurixNet pages that are server-rendered.

  2. **Second pass (JS-heavy)** — pages that trafilatura flags as low-quality
     get a Playwright re-fetch: `page.goto(url, wait_until='networkidle')`,
     then `page.content()` fed back through trafilatura.

  3. **Auth** — Nurix SSO. Playwright runs in "persistent context" mode with
     a stored user-data dir; first-run interactive login, subsequent runs
     reuse the session cookie. Store the user-data dir alongside the DPAPI
     config bundle.

  4. **Crawl discipline** — seed list + `robots.txt` respect, ~2-3 sec/page
     rate limit, `nurixnet_seen.json` for incremental runs.

  5. **Selector quarantine** — all NurixNet-specific CSS selectors live in
     `packages/jojo_ingest/_nurixnet_selectors.py` with per-selector tests
     and a fallback to raw-HTML-dump mode so we never silently lose content
     when a selector goes stale.

  6. **Asset handling** — `<img src="...">` rewriting to download images
     into `ask_jojo_raw/nurixnet/<article-id>/assets/` and point the
     markdown at the local path. (Karpathy's "download images locally" tip.)

Until VPN access + Playwright are set up, instantiating raises
NotImplementedError.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from jojo_connectors_common import Connector, SourceEntry


class NurixNetConnector(Connector):
    source_type = "nurixnet"

    def __init__(
        self,
        *,
        seed_urls: list[str] | None = None,
        user_data_dir: str = "",
    ) -> None:
        self.seed_urls = list(seed_urls or [])
        self.user_data_dir = user_data_dir

    def fetch(self, *, since: datetime | None = None) -> Iterable[SourceEntry]:
        raise NotImplementedError(
            "NurixNet connector is not wired yet. Blocked on VPN access "
            "and Playwright environment. See packages/jojo_ingest/nurixnet.py "
            "docstring for the implementation plan."
        )
