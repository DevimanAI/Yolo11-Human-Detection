#!/usr/bin/env python3
"""Download CrowdHuman annotations + only the images needed for training (not full 11 GB)."""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SLUG = "leducnhuan/crowdhuman"
RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "crowdhuman"
DEFAULT_MAX_TRAIN = 1532
DEFAULT_MAX_VAL = 383  # 1915 total — matches typical successful Kaggle subset download
MIN_OK_IMAGES = 1500
KAGGLE_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "kaggle.exe"
ANNOTATION_FILES = (
    ("CrowdHuman/annotation_train.odgt", "annotation_train.odgt"),
    ("CrowdHuman/annotation_val.odgt", "annotation_val.odgt"),
)


def kaggle_cmd() -> list[str]:
    if KAGGLE_EXE.exists():
        return [str(KAGGLE_EXE)]
    return ["kaggle"]


def run_kaggle_download(slug: str, kaggle_path: str, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        *kaggle_cmd(),
        "datasets",
        "download",
        "-d",
        slug,
        "-f",
        kaggle_path,
        "-p",
        str(dest_dir),
        "--unzip",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"Failed: {kaggle_path}")


def load_records(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def record_has_person(record: dict) -> bool:
    for gt in record.get("gtboxes", []):
        if gt.get("tag") not in {"person", "mask"}:
            continue
        if gt.get("vbox") or gt.get("fbox") or gt.get("hbox"):
            return True
    return False


def record_id(record: dict) -> str:
    if "ID" in record:
        return str(record["ID"])
    filepath = record.get("filepath", "")
    return Path(filepath).stem


def select_ids(records: list[dict], limit: int, seed: int) -> list[str]:
    eligible = [record_id(r) for r in records if record_has_person(r)]
    rng = random.Random(seed)
    rng.shuffle(eligible)
    return eligible[:limit]


def download_image(slug: str, split: str, image_id: str, raw_root: Path) -> tuple[str, bool, str]:
    folder = "Images" if split == "train" else "Images_val"
    filename = f"{image_id}.jpg"
    dest_dir = raw_root / folder
    dest_file = dest_dir / filename
    if dest_file.exists():
        return image_id, True, "exists"

    kaggle_path = f"CrowdHuman/{folder}/{filename}"
    try:
        run_kaggle_download(slug, kaggle_path, dest_dir)
    except Exception as exc:  # noqa: BLE001
        return image_id, False, str(exc)

    materialize_downloaded_file(dest_dir, filename)
    if dest_file.exists():
        return image_id, True, "downloaded"
    return image_id, False, "missing after download"


def materialize_downloaded_file(raw_root: Path, local_name: str) -> Path | None:
    """Kaggle often leaves *.zip without extracting; fix that before continuing."""
    target = raw_root / local_name
    if target.exists():
        return target

    search_roots = [raw_root, raw_root / "CrowdHuman"]
    for root in search_roots:
        nested = root / local_name
        if nested.exists():
            if nested != target:
                shutil.move(str(nested), str(target))
            return target

        zip_path = root / f"{local_name}.zip"
        if zip_path.exists():
            with zipfile.ZipFile(zip_path, "r") as archive:
                members = archive.namelist()
                archive.extractall(root)
            if target.exists():
                return target
            for member in members:
                member_path = root / member
                if member_path.is_file() and member_path.name == local_name:
                    if member_path != target:
                        shutil.move(str(member_path), str(target))
                    return target
    return None


def ensure_annotations(slug: str, raw_root: Path) -> None:
    raw_root.mkdir(parents=True, exist_ok=True)
    for _kaggle_path, local_name in ANNOTATION_FILES:
        materialized = materialize_downloaded_file(raw_root, local_name)
        if materialized is not None:
            continue
        print(f"Downloading {local_name} (~{'80' if 'train' in local_name else '23'} MB)...")
        run_kaggle_download(slug, f"CrowdHuman/{local_name}", raw_root)
        materialize_downloaded_file(raw_root, local_name)


def download_subset(
    slug: str,
    raw_root: Path,
    max_train: int,
    max_val: int,
    seed: int,
    workers: int,
) -> int:
    ensure_annotations(slug, raw_root)

    train_odgt = raw_root / "annotation_train.odgt"
    val_odgt = raw_root / "annotation_val.odgt"
    if not train_odgt.exists() or not val_odgt.exists():
        print("ERROR: annotation_train.odgt / annotation_val.odgt not found after download.")
        return 1

    train_ids = select_ids(load_records(train_odgt), max_train, seed)
    val_ids = select_ids(load_records(val_odgt), max_val, seed + 1)
    print(f"Selected {len(train_ids)} train + {len(val_ids)} val images (not the full 11 GB archive).")

    jobs: list[tuple[str, str]] = [("train", image_id) for image_id in train_ids]
    jobs.extend(("val", image_id) for image_id in val_ids)

    ok = 0
    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(download_image, slug, split, image_id, raw_root): (split, image_id)
            for split, image_id in jobs
        }
        for idx, future in enumerate(as_completed(futures), start=1):
            split, image_id = futures[future]
            _id, success, detail = future.result()
            if success:
                ok += 1
            else:
                failed.append(f"{split}:{image_id} ({detail})")
            if idx % 25 == 0 or idx == len(jobs):
                print(f"  Images: {idx}/{len(jobs)} ({ok} ok, {len(failed)} failed)")

    print(f"Done. {ok}/{len(jobs)} images in {raw_root}")
    if failed:
        print(f"WARNING: {len(failed)} image(s) failed (often Kaggle 429 rate limits). First 5:")
        for item in failed[:5]:
            print(f"  - {item}")
        if ok < MIN_OK_IMAGES:
            print(f"ERROR: only {ok} images downloaded; need at least {MIN_OK_IMAGES}.")
            return 1
        print(f"Continuing with {ok} downloaded images — convert will use what is on disk.")
    print("Next: .\\.venv\\Scripts\\python.exe scripts\\convert_crowdhuman.py")
    return 0


def download_full(slug: str, raw_root: Path) -> int:
    raw_root.mkdir(parents=True, exist_ok=True)
    cmd = [*kaggle_cmd(), "datasets", "download", "-d", slug, "-p", str(raw_root), "--unzip"]
    print("Downloading FULL dataset (~11 GB). This may take a long time...")
    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download CrowdHuman subset for YOLO training")
    parser.add_argument("--slug", default=DEFAULT_SLUG)
    parser.add_argument("--raw-root", type=Path, default=RAW_ROOT)
    parser.add_argument("--max-train", type=int, default=DEFAULT_MAX_TRAIN)
    parser.add_argument("--max-val", type=int, default=DEFAULT_MAX_VAL)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=2, help="Keep low to avoid Kaggle 429 rate limits")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Download entire Kaggle archive (~11 GB) instead of subset",
    )
    args = parser.parse_args()

    if not os.environ.get("KAGGLE_API_TOKEN") and not (Path.home() / ".kaggle" / "access_token").exists():
        print("ERROR: Set KAGGLE_API_TOKEN or create .kaggle/access_token in the repo.")
        return 1

    if args.full:
        return download_full(args.slug, args.raw_root)
    return download_subset(
        args.slug,
        args.raw_root,
        args.max_train,
        args.max_val,
        args.seed,
        args.workers,
    )


if __name__ == "__main__":
    sys.exit(main())
