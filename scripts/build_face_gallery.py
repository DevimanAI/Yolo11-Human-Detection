#!/usr/bin/env python3
"""Validate known_faces folders and report DeepFace gallery readiness."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.bootstrap import apply_project_env

apply_project_env()

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def scan_gallery(root: Path) -> dict:
    people: dict[str, list[Path]] = {}
    if not root.exists():
        return people
    for person_dir in sorted(root.iterdir()):
        if not person_dir.is_dir():
            continue
        images = [p for p in person_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS]
        if images:
            people[person_dir.name] = images
    return people


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect DeepFace known_faces gallery")
    parser.add_argument(
        "--dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "known_faces",
        help="Known faces root directory",
    )
    parser.add_argument("--build", action="store_true", help="Try loading DeepFace embeddings")
    args = parser.parse_args()

    gallery = scan_gallery(args.dir)
    if not gallery:
        print(f"No person folders with images under {args.dir}")
        print("Create: data/known_faces/YourName/photo.jpg")
        return 1

    total_images = sum(len(v) for v in gallery.values())
    print(f"Gallery root: {args.dir}")
    print(f"People: {len(gallery)} | Images: {total_images}")
    for name, images in gallery.items():
        print(f"  {name}: {len(images)} image(s)")

    if not args.build:
        print("\nInstall face extras: pip install -r requirements-face.txt")
        print("Then rerun with --build to verify embeddings.")
        return 0

    try:
        from app.face_registry import FaceRegistry
    except ImportError as exc:
        print(f"ERROR: {exc}")
        print("Install: .venv\\Scripts\\python.exe -m pip install -r requirements-face.txt")
        return 1

    registry = FaceRegistry(known_faces_dir=args.dir)
    if not registry.initialize():
        print("ERROR: DeepFace initialization failed.")
        return 1

    print(f"\nDeepFace ready — {registry.embedding_count} embedding(s) loaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
