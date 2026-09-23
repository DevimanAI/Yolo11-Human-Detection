#!/usr/bin/env python3
"""Fine-tune YOLO11n on the person dataset using configs/train_yolo11n.yaml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.env_check import abort_if_missing  # noqa: E402

abort_if_missing()


def load_train_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def materialize_dataset_yaml(data_yaml: Path) -> Path:
    """Write a generated dataset YAML with absolute paths (avoids Ultralytics path bugs)."""
    payload = yaml.safe_load(data_yaml.read_text(encoding="utf-8"))
    raw_path = Path(payload["path"])
    dataset_root = raw_path if raw_path.is_absolute() else (PROJECT_ROOT / raw_path).resolve()
    payload["path"] = str(dataset_root)
    generated = PROJECT_ROOT / "configs" / ".person_crowdhuman.generated.yaml"
    generated.write_text(yaml.dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description="Fine-tune YOLO11 for person detection")
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "configs" / "train_yolo11n.yaml",
        help="Training hyperparameter YAML",
    )
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--batch", type=int, default=None)
    parser.add_argument("--imgsz", type=int, default=None)
    parser.add_argument("--name", type=str, default=None)
    args = parser.parse_args()

    cfg = load_train_config(args.config)
    if args.epochs is not None:
        cfg["epochs"] = args.epochs
    if args.batch is not None:
        cfg["batch"] = args.batch
    if args.imgsz is not None:
        cfg["imgsz"] = args.imgsz
    if args.name is not None:
        cfg["name"] = args.name

    data_yaml = PROJECT_ROOT / cfg["data"]
    if not data_yaml.exists():
        print(f"ERROR: Dataset config not found: {data_yaml}")
        print("Run: scripts/download_dataset.ps1 && scripts/convert_crowdhuman.py")
        return 1

    data_yaml = materialize_dataset_yaml(data_yaml)
    dataset_root = Path(yaml.safe_load(data_yaml.read_text(encoding="utf-8"))["path"])
    train_images = dataset_root / "images" / "train"
    if not train_images.exists() or not any(train_images.glob("*")):
        print(f"ERROR: No training images in {train_images}")
        print("Convert CrowdHuman first: python scripts/convert_crowdhuman.py")
        return 1

    from ultralytics import YOLO  # noqa: E402

    model_path = cfg.pop("model")
    cfg.pop("data")
    cfg["data"] = str(data_yaml.resolve())
    cfg["project"] = str((PROJECT_ROOT / "runs" / "detect").resolve())

    weights = PROJECT_ROOT / model_path
    print(f"Loading weights: {weights}")
    print(f"Dataset: {cfg['data']}")
    print(f"Hyperparameters: {cfg}")

    model = YOLO(str(weights))
    results = model.train(**cfg)

    save_dir = Path(results.save_dir) if hasattr(results, "save_dir") else PROJECT_ROOT / cfg.get("project", "runs/detect") / cfg.get("name", "train")
    best = save_dir / "weights" / "best.pt"
    print(f"\nTraining complete.")
    if best.exists():
        print(f"Best weights: {best}")
        print(f"Use in .env: YOLO_MODEL={best.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"Metrics CSV: {save_dir / 'results.csv'}")
    print(f"Export for thesis: python scripts/export_metrics.py --run-dir {save_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
