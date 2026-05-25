#!/usr/bin/env python3
"""Compatibility wrapper for the packaged review policy."""

# ruff: noqa: E402,F403

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ai_training_tests.extraction.review.review_policy import *  # noqa: F403
