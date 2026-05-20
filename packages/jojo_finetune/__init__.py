"""jojo_finetune — fine-tune dataset generation, training pipeline, and eval harness.

Phase 8 of JoJo Bot v2.0.

Sub-modules:

- ``dataset`` — generate synthetic training examples from the wiki.
- ``train``   — submit / monitor fine-tune jobs against Bedrock or HuggingFace.
- ``eval``    — run evaluation against a benchmark set and score results.
- ``cli``     — ``jojo-finetune`` console script.
"""

from __future__ import annotations

__version__ = "0.1.0"
