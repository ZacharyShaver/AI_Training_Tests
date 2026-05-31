#!/usr/bin/env python3
"""Compatibility wrapper for the Plato Gorgias parser."""

# ruff: noqa: E402,F403,I001

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ai_training_tests.extraction.parsers.plato_gorgias import *  # noqa: F403
from ai_training_tests.extraction.parsers.plato_gorgias import main


if __name__ == "__main__":
    main()
