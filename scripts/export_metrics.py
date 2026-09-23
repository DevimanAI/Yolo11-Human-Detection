#!/usr/bin/env python3
"""Copy training artifacts into docs/training_runs/ for thesis and defense slides."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ARTIFACT_NAMES = (
    "results.csv",
    "results.png",
    "confusion_matrix.png",
    "confusion_matrix_normalized.png",
    "BoxPR_curve.png",
    "BoxF1_curve.png",
    "BoxP_curve.png",
    "BoxR_curve.png",
    "args.yaml",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export YOLO training metrics for documentation")
    parser.add_argument("--run-dir", type=Path, required=True, help="Ultralytics run dir, e.g. runs/detect/person_yolo11n")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Destination under docs/training_runs/ (auto-named if omitted)",
    )
    args = parser.parse_args()

    run_dir = args.run_dir if args.run_dir.is_absolute() else PROJECT_ROOT / args.run_dir
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        return 1

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = args.output_dir or (PROJECT_ROOT / "docs" / "training_runs" / f"{run_dir.name}_{stamp}")
    dest.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    for name in ARTIFACT_NAMES:
        source = run_dir / name
        if source.exists():
            shutil.copy2(source, dest / name)
            copied.append(name)

    weights = run_dir / "weights"
    if weights.exists():
        weights_dest = dest / "weights"
        weights_dest.mkdir(exist_ok=True)
        for weight in weights.glob("*.pt"):
            shutil.copy2(weight, weights_dest / weight.name)
            copied.append(f"weights/{weight.name}")

    summary: dict = {
        "run_dir": str(run_dir.relative_to(PROJECT_ROOT) if run_dir.is_relative_to(PROJECT_ROOT) else run_dir),
        "exported_at": stamp,
        "artifacts": copied,
    }

    results_csv = run_dir / "results.csv"
    if results_csv.exists():
        lines = results_csv.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) >= 2:
            headers = [h.strip() for h in lines[0].split(",")]
            last = [v.strip() for v in lines[-1].split(",")]
            summary["final_epoch"] = dict(zip(headers, last, strict=False))

    (dest / "export_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Exported {len(copied)} artifact(s) -> {dest}")
    print(json.dumps(summary.get("final_epoch", {}), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
