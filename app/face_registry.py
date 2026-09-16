from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class FaceRegistry:
    """Load known faces and match person crops using DeepFace embeddings."""

    def __init__(
        self,
        known_faces_dir: Path,
        model_name: str = "Facenet512",
        threshold: float = 0.4,
    ) -> None:
        self.known_faces_dir = known_faces_dir
        self.model_name = model_name
        self.threshold = threshold
        self._embeddings: list[tuple[str, np.ndarray]] = []
        self._deepface: Any | None = None
        self._available = False

    def initialize(self) -> bool:
        try:
            from deepface import DeepFace

            self._deepface = DeepFace
            self._load_known_faces()
            self._available = True
            logger.info("Face registry ready with %d known embedding(s)", len(self._embeddings))
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("Face recognition unavailable: %s", exc)
            self._available = False
            return False

    @property
    def available(self) -> bool:
        return self._available

    @property
    def embedding_count(self) -> int:
        return len(self._embeddings)

    def _load_known_faces(self) -> None:
        self._embeddings.clear()
        if not self.known_faces_dir.exists():
            self.known_faces_dir.mkdir(parents=True, exist_ok=True)
            return

        for person_dir in sorted(self.known_faces_dir.iterdir()):
            if not person_dir.is_dir():
                continue
            name = person_dir.name
            for image_path in sorted(person_dir.iterdir()):
                if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                embedding = self._embed(image_path)
                if embedding is not None:
                    self._embeddings.append((name, embedding))

    def _embed(self, source: Path | np.ndarray) -> np.ndarray | None:
        assert self._deepface is not None
        try:
            results = self._deepface.represent(
                img_path=str(source) if isinstance(source, Path) else source,
                model_name=self.model_name,
                enforce_detection=False,
            )
            if not results:
                return None
            return np.array(results[0]["embedding"], dtype=np.float32)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Failed to embed %s: %s", source, exc)
            return None

    @staticmethod
    def _cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 1.0
        return 1.0 - float(np.dot(a, b) / denom)

    def identify(self, person_crop_bgr: np.ndarray) -> str:
        if not self._available or not self._embeddings or person_crop_bgr.size == 0:
            return "Unknown"

        rgb = cv2.cvtColor(person_crop_bgr, cv2.COLOR_BGR2RGB)
        embedding = self._embed(rgb)
        if embedding is None:
            return "Unknown"

        best_name = "Unknown"
        best_distance = float("inf")
        for name, known_embedding in self._embeddings:
            distance = self._cosine_distance(embedding, known_embedding)
            if distance < best_distance:
                best_distance = distance
                best_name = name

        if best_distance <= self.threshold:
            return best_name
        return "Unknown"
