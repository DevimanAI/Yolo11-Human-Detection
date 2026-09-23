"""Pin Ultralytics and other tool paths to this repo (run after setup / before train)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE = PROJECT_ROOT / ".cache"


def ensure_dirs() -> None:
    for rel in (
        ".cache/pip",
        ".cache/torch",
        ".cache/ultralytics/weights",
        ".cache/huggingface",
        ".cache/tmp",
        "data/raw",
        "data/datasets",
        "runs",
        ".kaggle",
        ".deepface/weights",
    ):
        (PROJECT_ROOT / rel).mkdir(parents=True, exist_ok=True)


def apply_env() -> None:
    os.environ.setdefault("PIP_CACHE_DIR", str(CACHE / "pip"))
    os.environ.setdefault("TORCH_HOME", str(CACHE / "torch"))
    os.environ.setdefault("HF_HOME", str(CACHE / "huggingface"))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(CACHE / "huggingface"))
    os.environ.setdefault("KAGGLE_CONFIG_DIR", str(PROJECT_ROOT / ".kaggle"))
    os.environ.setdefault("ULTRALYTICS_CONFIG_DIR", str(CACHE / "ultralytics"))
    os.environ.setdefault("DEEPFACE_HOME", str(PROJECT_ROOT))
    tmp = CACHE / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("TEMP", str(tmp))
    os.environ.setdefault("TMP", str(tmp))


def configure_ultralytics() -> None:
    from ultralytics import settings

    settings.update(
        {
            "datasets_dir": str(PROJECT_ROOT / "data" / "datasets"),
            "weights_dir": str(CACHE / "ultralytics" / "weights"),
            "runs_dir": str(PROJECT_ROOT / "runs"),
        }
    )


def gpu_status() -> tuple[bool, str]:
    try:
        import torch

        if torch.cuda.is_available():
            return True, torch.cuda.get_device_name(0)
        return False, "CUDA not available (CPU-only PyTorch or no GPU driver)."
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def main() -> int:
    ensure_dirs()
    apply_env()
    configure_ultralytics()

    from ultralytics import settings

    print("Project root:", PROJECT_ROOT)
    print("Ultralytics datasets_dir:", settings["datasets_dir"])
    print("Ultralytics weights_dir:", settings["weights_dir"])
    print("Ultralytics runs_dir:", settings["runs_dir"])
    print("DEEPFACE_HOME:", os.environ.get("DEEPFACE_HOME"))
    print("PIP_CACHE_DIR:", os.environ.get("PIP_CACHE_DIR"))

    ok, detail = gpu_status()
    print("CUDA available:", ok)
    print("GPU:", detail if ok else detail)

    marker = PROJECT_ROOT / ".cache" / "project_configured.json"
    marker.write_text(
        json.dumps({"cuda": ok, "gpu": detail if ok else None}, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
