from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class FaceRegistry:
    """Match a person crop to a local gallery with DeepFace embeddings.

    The webcam crops are whole-person boxes, and OpenCV often misses the face
    when it is small. Embeddings are therefore taken from the upper body,
    where the face is, and a name is accepted only when cosine distance is
    clearly below the threshold. Strangers stay Unknown.
    """

    def __init__(
        self,
        known_faces_dir: Path,
        model_name: str = "Facenet512",
        threshold: float = 0.22,
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
            self._available = len(self._embeddings) > 0
            logger.info(
                "Face registry ready with %d known embedding(s), threshold=%.3f",
                len(self._embeddings),
                self.threshold,
            )
            return self._available
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
            if not person_dir.is_dir() or person_dir.name.startswith("_"):
                continue
            for image_path in sorted(person_dir.iterdir()):
                if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                image = cv2.imread(str(image_path))
                if image is None:
                    continue
                embedding = self._embed(self._upper_body(image))
                if embedding is None:
                    logger.warning("Skipping gallery image: %s", image_path.name)
                    continue
                self._embeddings.append((person_dir.name, embedding))

    @staticmethod
    def _upper_body(bgr: np.ndarray) -> np.ndarray:
        height = bgr.shape[0]
        return bgr[0 : max(1, int(height * 0.45)), :]

    def _embed(self, bgr: np.ndarray) -> np.ndarray | None:
        assert self._deepface is not None
        if bgr.size == 0 or bgr.shape[0] < 20 or bgr.shape[1] < 20:
            return None
        try:
            results = self._deepface.represent(
                img_path=bgr,
                model_name=self.model_name,
                enforce_detection=False,
                detector_backend="skip",
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Embedding failed: %s", exc)
            return None
        if not results:
            return None
        vector = np.array(results[0]["embedding"], dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm == 0:
            return None
        return vector / norm

    @staticmethod
    def _cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
        return 1.0 - float(np.dot(a, b))

    def identify(self, person_crop_bgr: np.ndarray) -> str:
        if not self._available or not self._embeddings or person_crop_bgr.size == 0:
            return "Unknown"

        embedding = self._embed(self._upper_body(person_crop_bgr))
        if embedding is None:
            return "Unknown"

        best_name = "Unknown"
        best_distance = float("inf")
        for name, known in self._embeddings:
            distance = self._cosine_distance(embedding, known)
            if distance < best_distance:
                best_distance = distance
                best_name = name

        if best_distance <= self.threshold:
            return best_name
        return "Unknown"