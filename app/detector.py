from __future__ import annotations

import logging
from dataclasses import dataclass
import cv2
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)

PERSON_CLASS_ID = 0


@dataclass
class TrackedPerson:
    track_id: int
    bbox: tuple[int, int, int, int]
    confidence: float
    label: str = "person"


class HumanDetectorTracker:
    """Ultralytics YOLO person detection with ByteTrack / BoT-SORT tracking."""

    def __init__(
        self,
        model_path: str,
        tracker: str,
        confidence: float,
    ) -> None:
        self.model_path = model_path
        self.tracker = tracker
        self.confidence = confidence
        self.model = YOLO(model_path)
        logger.info("Loaded YOLO model %s with tracker %s", model_path, tracker)

    def process_frame(self, frame_bgr: np.ndarray) -> list[TrackedPerson]:
        results = self.model.track(
            source=frame_bgr,
            persist=True,
            tracker=self.tracker,
            classes=[PERSON_CLASS_ID],
            conf=self.confidence,
            verbose=False,
        )

        tracked: list[TrackedPerson] = []
        if not results:
            return tracked

        result = results[0]
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return tracked

        xyxy = boxes.xyxy.cpu().numpy()
        confidences = boxes.conf.cpu().numpy()
        ids = boxes.id
        track_ids = ids.cpu().numpy().astype(int) if ids is not None else np.arange(len(xyxy))

        height, width = frame_bgr.shape[:2]
        for idx, (box, conf, track_id) in enumerate(zip(xyxy, confidences, track_ids, strict=True)):
            x1, y1, x2, y2 = [int(v) for v in box]
            x1 = max(0, min(x1, width - 1))
            x2 = max(0, min(x2, width))
            y1 = max(0, min(y1, height - 1))
            y2 = max(0, min(y2, height))
            if x2 <= x1 or y2 <= y1:
                continue
            tracked.append(
                TrackedPerson(
                    track_id=int(track_id),
                    bbox=(x1, y1, x2, y2),
                    confidence=float(conf),
                )
            )
        return tracked

    @staticmethod
    def draw_annotations(frame_bgr: np.ndarray, people: list[TrackedPerson]) -> np.ndarray:
        output = frame_bgr.copy()
        for person in people:
            x1, y1, x2, y2 = person.bbox
            color = _track_color(person.track_id)
            cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
            caption = f"ID {person.track_id} | {person.label} ({person.confidence:.2f})"
            _draw_label(output, caption, x1, y1, color)
        return output


def _track_color(track_id: int) -> tuple[int, int, int]:
    rng = np.random.default_rng(track_id + 42)
    return tuple(int(v) for v in rng.integers(64, 255, size=3))


def _draw_label(frame: np.ndarray, text: str, x: int, y: int, color: tuple[int, int, int]) -> None:
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.55
    thickness = 2
    (text_w, text_h), baseline = cv2.getTextSize(text, font, scale, thickness)
    top = max(y - text_h - baseline - 6, 0)
    cv2.rectangle(frame, (x, top), (x + text_w + 8, top + text_h + baseline + 6), color, -1)
    cv2.putText(frame, text, (x + 4, top + text_h + 2), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)
