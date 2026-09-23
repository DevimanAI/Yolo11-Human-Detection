from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from app.bootstrap import PROJECT_ROOT, apply_project_env

apply_project_env()
load_dotenv()


def _resolve_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


@dataclass(frozen=True)
class Settings:
    yolo_model: str = os.getenv("YOLO_MODEL", "yolo11n.pt")
    tracker: str = os.getenv("TRACKER", "bytetrack.yaml")
    video_source: str = os.getenv("VIDEO_SOURCE", "0")
    confidence: float = float(os.getenv("CONFIDENCE", "0.5"))
    face_recognition_enabled: bool = os.getenv("FACE_RECOGNITION_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
    }
    known_faces_dir: Path = _resolve_path(os.getenv("KNOWN_FACES_DIR", "data/known_faces"))
    face_match_threshold: float = float(os.getenv("FACE_MATCH_THRESHOLD", "0.4"))
    face_model: str = os.getenv("FACE_MODEL", "Facenet512")
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8765"))

    @property
    def yolo_model_path(self) -> str:
        path = Path(self.yolo_model)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return str(path.resolve())

    @property
    def parsed_video_source(self) -> int | str:
        if self.video_source.isdigit():
            return int(self.video_source)
        return str(_resolve_path(self.video_source))


settings = Settings()
