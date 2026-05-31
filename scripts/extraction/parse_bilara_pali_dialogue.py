#!/usr/bin/env python3
"""CLI wrapper for the bilara Pali Canon dialogue parser.

Reads from the local bilara-data clone at
source_texts/buddhist/raw/bilara-data/ — no network calls.

Usage:
    python scripts/extraction/parse_bilara_pali_dialogue.py
    python scripts/extraction/parse_bilara_pali_dialogue.py --collections dn sn1-11
    python scripts/extraction/parse_bilara_pali_dialogue.py --uids dn23 sn3.1
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
TOOLS_ROOT = REPO_ROOT / "tools"
for p in (str(SRC_ROOT), str(TOOLS_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from ai_training_tests.extraction.parsers.bilara_pali_dialogue import main

if __name__ == "__main__":
    main()
