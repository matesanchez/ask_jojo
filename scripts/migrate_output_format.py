#!/usr/bin/env python3
"""Backfill output_format: markdown for outputs/ pages missing the field."""
import re
import sys
from pathlib import Path


def main() -> int:
    wiki_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parents[2] / "ask_jojo_wiki"
    outputs_dir = wiki_root / "outputs"
    if not outputs_dir.exists():
        print("outputs/ directory not found; nothing to migrate.")
        return 0

    patched = 0
    for md_file in sorted(outputs_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        # Check if already has output_format
        if re.search(r"^output_format:", text, re.MULTILINE):
            continue
        # Insert output_format: markdown after the type: output line
        new_text = re.sub(
            r"(^type: output\s*$)",
            r"\1\noutput_format: markdown",
            text,
            flags=re.MULTILINE,
        )
        if new_text != text:
            md_file.write_text(new_text, encoding="utf-8")
            patched += 1
            print(f"  patched {md_file.name}")
    print(f"Migration complete: {patched} files patched.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
