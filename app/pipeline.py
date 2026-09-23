from __future__ import annotations

import logging
import threading
import time
from typing import Generator

import cv2
import numpy as np

from app.config import Settings, settings
from app.detector import HumanDetectorTracker, TrackedPerson
from app.face_registry import FaceRegistry

logger = logging.getLogger(__name__)


class VideoPipeline:
    """Capture video, run YOLO tracking, optionally identify faces."""

    def __init__(self, cfg: Settings | None = None) -> None:
        self.cfg = cfg or settings
        self.detector = HumanDetectorTracker(
            model_path=self.cfg.yolo_model_path,
            tracker=self.cfg.tracker,
            confidence=self.cfg.confidence,
        )
        self.face_registry: FaceRegistry | None = None
        if self.cfg.face_recognition_enabled:
            registry = FaceRegistry(
                known_faces_dir=self.cfg.known_faces_dir,
                model_name=self.cfg.face_model,
                threshold=self.cfg.face_match_threshold,
            )
            if registry.initialize():
                self.face_registry = registry

        self._capture: cv2.VideoCapture | None = None
        self._lock = threading.Lock()
        self._running = False
        self._identity_cache: dict[int, tuple[str, float]] = {}
        self._identity_ttl_seconds = 2.0
        self._stats = {
            "fps": 0.0,
            "person_count": 0,
            "frame_count": 0,
            "face_recognition": self.face_registry is not None,
        }

    def open_source(self, source: int | str | None = None) -> None:
        self.close()
        video_source = source if source is not None else self.cfg.parsed_video_source
        capture = cv2.VideoCapture(video_source)
        if not capture.isOpened():
            raise RuntimeError(f"Unable to open video source: {video_source}")
        self._capture = capture
        logger.info("Opened video source: %s", video_source)

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def _apply_face_labels(self, frame: np.ndarray, people: list[TrackedPerson]) -> None:
        if self.face_registry is None:
            return

        now = time.time()
        for person in people:
            cached = self._identity_cache.get(person.track_id)
            if cached and now - cached[1] < self._identity_ttl_seconds:
                person.label = cached[0]
                continue

            x1, y1, x2, y2 = person.bbox
            crop = frame[y1:y2, x1:x2]
            name = self.face_registry.identify(crop)
            person.label = name
            self._identity_cache[person.track_id] = (name, now)

    def read_frame(self) -> np.ndarray | None:
        if self._capture is None:
            self.open_source()
        assert self._capture is not None
        ok, frame = self._capture.read()
        if not ok:
            return None
        return frame

    def process_once(self) -> tuple[np.ndarray | None, dict]:
        frame = self.read_frame()
        if frame is None:
            return None, dict(self._stats)

        start = time.perf_counter()
        people = self.detector.process_frame(frame)
        self._apply_face_labels(frame, people)
        annotated = self.detector.draw_annotations(frame, people)

        elapsed = time.perf_counter() - start
        self._stats["fps"] = 1.0 / elapsed if elapsed > 0 else 0.0
        self._stats["person_count"] = len(people)
        self._stats["frame_count"] += 1
        return annotated, dict(self._stats)

    def mjpeg_stream(self) -> Generator[bytes, None, None]:
        self._running = True
        try:
            while self._running:
                with self._lock:
                    frame, stats = self.process_once()
                if frame is None:
                    break
                ok, encoded = cv2.imencode(
                    ".jpg",
                    frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), 80],
                )
                if not ok:
                    continue
                payload = encoded.tobytes()
                header = (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                )
                yield header + payload + b"\r\n"
        finally:
            self.close()

    def stop(self) -> None:
        self._running = False

    def get_status(self) -> dict:
        return {
            **self._stats,
            "model": self.cfg.yolo_model,
            "tracker": self.cfg.tracker,
            "video_source": str(self.cfg.video_source),
            "known_faces_dir": str(self.cfg.known_faces_dir),
            "known_faces_loaded": self.face_registry.embedding_count if self.face_registry else 0,
        }
