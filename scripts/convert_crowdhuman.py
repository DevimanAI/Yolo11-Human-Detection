#!/usr/bin/env python3
"""Convert CrowdHuman ODGT annotations to Ultralytics YOLO format (single class: person)."""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "crowdhuman"
OUTPUT_ROOT = PROJECT_ROOT / "data" / "datasets" / "person_crowdhuman"


def find_odgt_files(raw_root: Path) -> tuple[Path | None, Path | None]:
    train = None
    val = None
    for path in raw_root.rglob("*.odgt"):
        name = path.name.lower()
        if "train" in name:
            train = path
        elif "val" in name:
            val = path
    if train is None:
        candidates = list(raw_root.rglob("annotation_train.odgt"))
        train = candidates[0] if candidates else None
    if val is None:
        candidates = list(raw_root.rglob("annotation_val.odgt"))
        val = candidates[0] if candidates else None
    return train, val


def find_image(raw_root: Path, filepath: str) -> Path | None:
    filename = Path(filepath).name
    for candidate in (
        raw_root / "Images" / filename,
        raw_root / "images" / filename,
        raw_root / filename,
    ):
        if candidate.exists():
            return candidate
    matches = list(raw_root.rglob(filename))
    return matches[0] if matches else None


def box_to_yolo(box: list[float], width: int, height: int) -> tuple[float, float, float, float] | None:
    if len(box) != 4:
        return None
    x, y, w, h = box
    if w <= 1 or h <= 1:
        return None
    x_center = (x + w / 2) / width
    y_center = (y + h / 2) / height
    norm_w = w / width
    norm_h = h / height
    if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and norm_w <= 1 and norm_h <= 1):
        return None
    return x_center, y_center, norm_w, norm_h


def parse_record(record: dict) -> tuple[str, int, int, list[tuple[float, float, float, float]]]:
    filepath = record["filepath"]
    width = int(record["width"])
    height = int(record["height"])
    boxes: list[tuple[float, float, float, float]] = []
    for gt in record.get("gtboxes", []):
        if gt.get("tag") not in {"person", "mask"}:
            continue
        raw_box = gt.get("vbox") or gt.get("fbox") or gt.get("hbox")
        if raw_box is None:
            continue
        yolo_box = box_to_yolo(raw_box, width, height)
        if yolo_box is not None:
            boxes.append(yolo_box)
    return filepath, width, height, boxes


def convert_split(
    odgt_path: Path,
    raw_root: Path,
    split: str,
    output_root: Path,
    max_images: int | None,
    seed: int,
) -> tuple[int, int]:
    image_dir = output_root / "images" / split
    label_dir = output_root / "labels" / split
    image_dir.mkdir(parents=True, exist_ok=True)
    label_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    with odgt_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

    rng = random.Random(seed)
    rng.shuffle(records)
    if max_images is not None:
        records = records[:max_images]

    saved = 0
    skipped = 0
    for record in records:
        filepath, _width, _height, boxes = parse_record(record)
        if not boxes:
            skipped += 1
            continue
        source = find_image(raw_root, filepath)
        if source is None:
            skipped += 1
            continue

        stem = Path(filepath).stem
        dest_image = image_dir / f"{stem}{source.suffix.lower()}"
        dest_label = label_dir / f"{stem}.txt"

        shutil.copy2(source, dest_image)
        lines = [f"0 {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}" for xc, yc, w, h in boxes]
        dest_label.write_text("\n".join(lines) + "\n", encoding="utf-8")
        saved += 1

    return saved, skipped


def build_mini_from_sample(output_root: Path) -> int:
    """Fallback: pseudo-label bus.jpg with pretrained YOLO for smoke training."""
    from app.env_check import abort_if_missing

    abort_if_missing()
    from ultralytics import YOLO

    sample = PROJECT_ROOT / "data" / "sample" / "bus.jpg"
    if not sample.exists():
        raise SystemExit("Mini dataset needs data/sample/bus.jpg — run smoke_test.py first.")

    model = YOLO(str(PROJECT_ROOT / "yolo11n.pt"))
    results = model.predict(source=str(sample), conf=0.25, classes=[0], verbose=False)
    if not results or results[0].boxes is None:
        raise SystemExit("Could not pseudo-label bus.jpg")

    import cv2

    frame = cv2.imread(str(sample))
    if frame is None:
        raise SystemExit(f"Could not read {sample}")

    height, width = frame.shape[:2]
    boxes = results[0].boxes.xyxy.cpu().numpy()

    for split, copies in (("train", 8), ("val", 2)):
        image_dir = output_root / "images" / split
        label_dir = output_root / "labels" / split
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)
        for idx in range(copies):
            stem = f"bus_{split}_{idx}"
            dest_image = image_dir / f"{stem}.jpg"
            dest_label = label_dir / f"{stem}.txt"
            shutil.copy2(sample, dest_image)
            lines: list[str] = []
            for box in boxes:
                x1, y1, x2, y2 = box
                yolo = box_to_yolo([x1, y1, x2 - x1, y2 - y1], width, height)
                if yolo:
                    xc, yc, w, h = yolo
                    lines.append(f"0 {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")
            dest_label.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return 10


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert CrowdHuman to YOLO person dataset")
    parser.add_argument("--raw-root", type=Path, default=RAW_ROOT)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--max-train", type=int, default=2000, help="Max train images (default 2000)")
    parser.add_argument("--max-val", type=int, default=500, help="Max val images (default 500)")
    parser.add_argument("--mini", action="store_true", help="Build tiny pseudo-labeled set from bus.jpg")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.mini:
        count = build_mini_from_sample(args.output_root)
        print(f"Mini dataset ready: {count} images -> {args.output_root}")
        return 0

    train_odgt, val_odgt = find_odgt_files(args.raw_root)
    if train_odgt is None or val_odgt is None:
        print(f"ERROR: CrowdHuman ODGT files not found under {args.raw_root}")
        print("Run scripts/download_dataset.ps1 or place annotation_train.odgt / annotation_val.odgt manually.")
        print("For smoke training without Kaggle: python scripts/convert_crowdhuman.py --mini")
        return 1

    if args.output_root.exists():
        shutil.rmtree(args.output_root)
    args.output_root.mkdir(parents=True, exist_ok=True)

    train_saved, train_skipped = convert_split(
        train_odgt, args.raw_root, "train", args.output_root, args.max_train, args.seed
    )
    val_saved, val_skipped = convert_split(
        val_odgt, args.raw_root, "val", args.output_root, args.max_val, args.seed + 1
    )

    print(f"Train: saved={train_saved} skipped={train_skipped} (limit {args.max_train})")
    print(f"Val:   saved={val_saved} skipped={val_skipped} (limit {args.max_val})")
    print(f"YOLO dataset -> {args.output_root}")
    print(f"Config -> configs/person_crowdhuman.yaml")
    if train_saved == 0:
        print("ERROR: No training images converted.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
