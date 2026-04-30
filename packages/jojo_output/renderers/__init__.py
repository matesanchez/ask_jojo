"""Output renderers — typed-spec to artifact converters.

Each renderer accepts a typed spec (Pydantic model) and produces a
file or in-memory bytes. The model authors the spec; the renderer
authors the artifact. Same contract as the sandbox: model produces
data, renderer produces output.

The matplotlib path lives in ``../sandbox/`` because it has security
requirements the other renderers don't (the ``data spec plus
plot-type choice`` is rendered by Python that runs subprocesses with
rlimit). The renderers in this package handle formats where the
underlying library is safe to run in-process.

Public API:

- ``render_table(TableSpec) -> dict[fmt, bytes]``
- ``render_marp(MarpSpec) -> bytes``     (the markdown body; the SVG
                                          carousel render happens
                                          frontend-side via the Web
                                          Worker)
- ``render_docx(DocxSpec, out_path)``
- ``render_pptx(PptxSpec, out_path)``
- ``render_pdf(PdfSpec, out_path)``
- ``render_markdown(MarkdownSpec)``

Each ``Spec`` is a Pydantic model. The cross-renderer plumbing
(format dispatch, file-back, asset paths) lives in
``output_router.py``.
"""

from .markdown import MarkdownSpec, render_markdown
from .marp import MarpSpec, render_marp
from .table import TableSpec, render_table

# docx/pptx/pdf renderers depend on optional libraries (python-docx,
# python-pptx, weasyprint). Import lazily so the package is usable
# without them installed.

__all__ = [
    "MarkdownSpec",
    "MarpSpec",
    "TableSpec",
    "render_markdown",
    "render_marp",
    "render_table",
]
