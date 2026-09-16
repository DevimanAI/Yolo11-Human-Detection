#!/usr/bin/env python3
"""Launch the web demo."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.env_check import abort_if_missing

abort_if_missing()

from app.main import run

if __name__ == "__main__":
    run()
