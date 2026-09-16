#!/usr/bin/env python3
"""Smoke test: download YOLO weights and run person detection on a sample image."""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

SAMPLE_URL = "https://ultralytics.com/images/bus.jpg"
SAMPLE_PATH = PROJECT_ROOT / "data" / "sample" / "bus.jpg"


def download_sample() -> Path:
    SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not SAMPLE_PATH.exists():
        print(f"Downloading sample image -> {SAMPLE_PATH}")
        urllib.request.urlretrieve(SAMPLE_URL, SAMPLE_PATH)
    return SAMPLE_PATH


def main() -> int:
    from app.detector import HumanDetectorTracker

    image_path = download_sample()
    frame = cv2.imread(str(image_path))
    if frame is None:
        print("ERROR: Could not read sample image")
        return 1

    detector = HumanDetectorTracker("yolo11n.pt", "bytetrack.yaml", confidence=0.4)
    people = detector.process_frame(frame)
    annotated = detector.draw_annotations(frame, people)

    output_path = PROJECT_ROOT / "data" / "sample" / "bus_detected.jpg"
    cv2.imwrite(str(output_path), annotated)

    print(f"Detected {len(people)} person(s)")
    for person in people:
        print(f"  track_id={person.track_id} conf={person.confidence:.2f} bbox={person.bbox}")
    print(f"Saved annotated output -> {output_path}")
    return 0 if people else 1


if __name__ == "__main__":
    raise SystemExit(main())
