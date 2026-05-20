# JoJo Bot v2.0 License Inventory

**Date:** 2026-05-20

Sources: `pyproject.toml` (Python) and `src/frontend/package.json` (Node).
Licenses sourced from training-data knowledge of published package metadata.
"CHECK" means the package is uncommon enough that the license could not be
confirmed from training data; verify with `pip show <pkg>` or PyPI.

---

## Python dependencies (pyproject.toml)

### [dev] optional group

| Package | Version pin | License | Compatible |
|---------|-------------|---------|-----------|
| ruff | >=0.4.0 | MIT | ✓ |
| pytest | >=8.0 | MIT | ✓ |
| pytest-cov | >=5.0 | MIT | ✓ |
| pytest-httpx | >=0.30 | MIT | ✓ |
| python-docx | >=1.1 | MIT | ✓ |

### [backend] optional group

| Package | Version pin | License | Compatible |
|---------|-------------|---------|-----------|
| fastapi | >=0.110 | MIT | ✓ |
| uvicorn[standard] | >=0.27 | BSD-3-Clause | ✓ |
| redis | >=5.0 | MIT | ✓ |
| rq | >=1.16 | BSD-2-Clause | ✓ |
| python-multipart | >=0.0.9 | Apache-2.0 | ✓ |
| anthropic | >=0.40 | MIT | ✓ |
| msal | >=1.27 | MIT | ✓ |

### [ingest] optional group

| Package | Version pin | License | Compatible |
|---------|-------------|---------|-----------|
| pyyaml | >=6.0 | MIT | ✓ |
| mammoth | >=1.7 | BSD-2-Clause | ✓ |
| python-pptx | >=0.6.23 | MIT | ✓ |
| openpyxl | >=3.1 | MIT | ✓ |
| pymupdf | >=1.24 | AGPL-3.0 | **ATTENTION** |
| watchdog | >=4.0 | Apache-2.0 | ✓ |

### [cloud] optional group

| Package | Version pin | License | Compatible |
|---------|-------------|---------|-----------|
| msgraph-core | >=1.0 | MIT | ✓ |
| azure-identity | >=1.15 | MIT | ✓ |
| httpx | >=0.27 | BSD-3-Clause | ✓ |
| msal | >=1.27 | MIT | ✓ |

### [web] optional group

| Package | Version pin | License | Compatible |
|---------|-------------|---------|-----------|
| playwright | >=1.42 | Apache-2.0 | ✓ |
| trafilatura | >=1.9 | Apache-2.0 | ✓ |
| html2text | >=2024.2.26 | GPL-3.0 | **ATTENTION** |

### [qa] optional group

| Package | Version pin | License | Compatible |
|---------|-------------|---------|-----------|
| qmd | >=0.3 | CHECK | CHECK |
| anthropic | >=0.40 | MIT | ✓ |
| pydantic | >=2.6 | MIT | ✓ |

### [lint] optional group

| Package | Version pin | License | Compatible |
|---------|-------------|---------|-----------|
| pyyaml | >=6.0 | MIT | ✓ |

### [finetune] optional group

| Package | Version pin | License | Compatible |
|---------|-------------|---------|-----------|
| boto3 | >=1.26 | Apache-2.0 | ✓ |
| peft | >=0.10 | Apache-2.0 | ✓ |
| transformers | >=4.40 | Apache-2.0 | ✓ |
| trl | >=0.8 | Apache-2.0 | ✓ |
| datasets | >=2.18 | Apache-2.0 | ✓ |

### [output] optional group

| Package | Version pin | License | Compatible |
|---------|-------------|---------|-----------|
| matplotlib | >=3.8 | PSF / BSD-compatible | ✓ |
| numpy | >=1.26 | BSD-3-Clause | ✓ |
| pandas | >=2.2 | BSD-3-Clause | ✓ |
| seaborn | >=0.13 | BSD-3-Clause | ✓ |
| plotly | >=5.20 | MIT | ✓ |
| python-docx | >=1.1 | MIT | ✓ |
| python-pptx | >=0.6.23 | MIT | ✓ |
| weasyprint | >=61 | BSD-3-Clause | ✓ |
| markdown | >=3.6 | BSD-3-Clause | ✓ |

---

## Node dependencies (package.json)

### dependencies

| Package | Version pin | License | Compatible |
|---------|-------------|---------|-----------|
| @marp-team/marp-core | ^4.0.0 | MIT | ✓ |
| @types/three | ^0.184.1 | MIT | ✓ |
| chart.js | ^4.5.1 | MIT | ✓ |
| highlight.js | ^11.11.1 | BSD-3-Clause | ✓ |
| mermaid | ^11.4.0 | MIT | ✓ |
| next | ^14.2.3 | MIT | ✓ |
| react | ^18.3.1 | MIT | ✓ |
| react-chartjs-2 | ^5.3.1 | MIT | ✓ |
| react-dom | ^18.3.1 | MIT | ✓ |
| react-markdown | ^9.0.1 | MIT | ✓ |
| rehype-highlight | ^7.0.2 | MIT | ✓ |
| remark-gfm | ^4.0.0 | MIT | ✓ |
| remark-wiki-link | ^2.0.1 | MIT | ✓ |
| three | ^0.157.0 | MIT | ✓ |

### devDependencies

| Package | Version pin | License | Compatible |
|---------|-------------|---------|-----------|
| @types/node | ^20.12.0 | MIT | ✓ |
| @types/react | ^18.3.0 | MIT | ✓ |
| @types/react-dom | ^18.3.0 | MIT | ✓ |
| eslint | ^8.57.0 | MIT | ✓ |
| eslint-config-next | ^14.2.3 | MIT | ✓ |
| typescript | ^5.4.5 | Apache-2.0 | ✓ |

---

## Assessment

The vast majority of dependencies use MIT, Apache-2.0, or BSD licenses, which
are compatible with proprietary / commercial use.

### ATTENTION items — RESOLVED 2026-05-20

Legal confirmed (verbal, Mateo de los Rios, 2026-05-20): JoJo Bot is internal-only, never distributed to customers, and not offered as a network service to external parties. Both copyleft licenses are acceptable under this use case. No replacement required.

| Package | License | Resolution |
|---------|---------|-----------|
| **pymupdf** (PyMuPDF) | AGPL-3.0 | **CLEARED** — Legal confirmed internal-only distribution does not trigger AGPL copyleft. FU-23 closed. |
| **html2text** | GPL-3.0 | **CLEARED** — Legal confirmed internal-only deployment is not a distribution or network-service scenario under GPL-3.0. FU-23 closed. |

### CHECK items (license unconfirmed)

| Package | Reason |
|---------|--------|
| **qmd** | Package is referenced in the spec doc as "Karpathy's local BM25 + vector over markdown" but is not widely indexed. License cannot be confirmed from training data. Run `pip show qmd` or check its PyPI page before activating the [qa] optional group. |
