#!/usr/bin/env python3
"""Smoke test: download YOLO weights and run person detection on a sample image."""

from __future__ import annotations

import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.env_check import abort_if_missing  # noqa: E402

abort_if_missing()

import cv2  # noqa: E402

from app.detector import HumanDetectorTracker  # noqa: E402

SAMPLE_URL = "https://ultralytics.com/images/bus.jpg"
SAMPLE_PATH = PROJECT_ROOT / "data" / "sample" / "bus.jpg"


def download_sample() -> Path:
    SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SAMPLE_PATH.exists():
        return SAMPLE_PATH

    print(f"Downloading sample image -> {SAMPLE_PATH}")
    request = urllib.request.Request(
        SAMPLE_URL,
        headers={"User-Agent": "Yolo11-Human-Detection-smoke-test"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            SAMPLE_PATH.write_bytes(response.read())
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"ERROR: Could not download sample image from {SAMPLE_URL}: {exc}")
        print("Check your network connection and retry.")
        raise SystemExit(1) from exc
    return SAMPLE_PATH


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Smoke test person detection")
    parser.add_argument("--model", default="yolo11n.pt", help="YOLO weights path")
    parser.add_argument("--confidence", type=float, default=0.4)
    args = parser.parse_args()

    image_path = download_sample()
    frame = cv2.imread(str(image_path))
    if frame is None:
        print(f"ERROR: Could not read sample image at {image_path}")
        return 1

    detector = HumanDetectorTracker(args.model, "bytetrack.yaml", confidence=args.confidence)
    people = detector.process_frame(frame)
    annotated = detector.draw_annotations(frame, people)

    output_path = PROJECT_ROOT / "data" / "sample" / "bus_detected.jpg"
    if not cv2.imwrite(str(output_path), annotated):
        print(f"ERROR: Could not write annotated image to {output_path}")
        return 1

    print(f"Detected {len(people)} person(s)")
    for person in people:
        print(f"  track_id={person.track_id} conf={person.confidence:.2f} bbox={person.bbox}")
    print(f"Saved annotated output -> {output_path}")
    if not people:
        print("ERROR: Expected at least one person on the bus sample image.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
