from pathlib import Path
from typing import Optional, Tuple

import cv2
import mss
import numpy as np

from core.config import AppConfig


class VisionEngine:
    def __init__(self, config: AppConfig):
        self._config = config
        self._ocr = None
        self._sct = None

    def _get_ocr(self):
        if self._ocr is None:
            from paddleocr import PaddleOCR

            self._ocr = PaddleOCR(use_angle_cls=True, lang="chinese_cht")
        return self._ocr

    def capture_screen(self) -> np.ndarray:
        sct = mss.mss()
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        try:
            frame = np.array(screenshot)
        except TypeError:
            # Fallback for environments where __array__ has non-standard signature
            frame = screenshot.__array__(screenshot)
        sct.close()
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def find_template(
        self,
        scene: np.ndarray,
        template: np.ndarray,
        threshold: Optional[float] = None,
    ) -> Optional[Tuple[int, int, float]]:
        if threshold is None:
            threshold = self._config.vision.template_threshold

        # Try color match first using normalized cross-correlation
        result = cv2.matchTemplate(scene, template, cv2.TM_CCORR_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        h, w = template.shape[:2]

        if max_val >= threshold:
            center_x = int(max_loc[0]) + w // 2
            center_y = int(max_loc[1]) + h // 2
            return (center_x, center_y, float(max_val))

        # Fallback to grayscale
        scene_gray = cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(scene_gray, template_gray, cv2.TM_CCORR_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold * 0.9:  # slightly lower threshold for grayscale
            center_x = int(max_loc[0]) + w // 2
            center_y = int(max_loc[1]) + h // 2
            return (center_x, center_y, float(max_val))

        return None

    def find_text(
        self,
        scene: np.ndarray,
        target_text: str,
        confidence_threshold: Optional[float] = None,
    ) -> Optional[Tuple[int, int, float]]:
        if confidence_threshold is None:
            confidence_threshold = self._config.vision.ocr_confidence

        ocr = self._get_ocr()
        results = ocr.ocr(scene, cls=True)

        if not results or not results[0]:
            return None

        for line in results[0]:
            box, (text, confidence) = line
            if target_text in text and confidence >= confidence_threshold:
                # Calculate center of bounding box
                xs = [point[0] for point in box]
                ys = [point[1] for point in box]
                center_x = int(sum(xs) / len(xs))
                center_y = int(sum(ys) / len(ys))
                return (center_x, center_y, confidence)

        return None

    def find_element(
        self,
        scene: np.ndarray,
        text: Optional[str] = None,
        template: Optional[np.ndarray] = None,
    ) -> Optional[Tuple[int, int, float]]:
        # Try OCR first if text is provided
        if text:
            result = self.find_text(scene, text)
            if result:
                return result

        # Fall back to template matching
        if template is not None:
            result = self.find_template(scene, template)
            if result:
                return result

        return None

    def load_template(self, path: Path) -> np.ndarray:
        template = cv2.imread(str(path))
        if template is None:
            raise FileNotFoundError(f"Template not found: {path}")
        return template

    def save_screenshot(self, scene: np.ndarray, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(path), scene)
