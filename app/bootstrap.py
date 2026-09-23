"""Apply project-local env before DeepFace / Ultralytics imports."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def apply_project_env() -> None:
    cache = PROJECT_ROOT / ".cache"
    cache.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("DEEPFACE_HOME", str(PROJECT_ROOT))
    os.environ.setdefault("PIP_CACHE_DIR", str(cache / "pip"))
    os.environ.setdefault("TORCH_HOME", str(cache / "torch"))
    os.environ.setdefault("ULTRALYTICS_CONFIG_DIR", str(cache / "ultralytics"))

    (PROJECT_ROOT / ".deepface" / "weights").mkdir(parents=True, exist_ok=True)
