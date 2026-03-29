import numpy as np
import cv2
from unittest.mock import patch, MagicMock
from pathlib import Path

from core.vision import VisionEngine
from core.config import AppConfig


class TestScreenshot:
    def test_capture_returns_numpy_array(self):
        config = AppConfig()
        engine = VisionEngine(config)
        mock_sct = MagicMock()
        mock_sct.grab.return_value = MagicMock(
            pixels=None, size=MagicMock(width=1920, height=1080)
        )
        mock_sct.grab.return_value.__array__ = lambda self: np.zeros(
            (1080, 1920, 4), dtype=np.uint8
        )
        with patch("core.vision.mss.mss", return_value=mock_sct):
            screenshot = engine.capture_screen()
        assert isinstance(screenshot, np.ndarray)
        assert screenshot.shape[0] == 1080
        assert screenshot.shape[1] == 1920


class TestTemplateMatching:
    def test_find_template_returns_location_when_found(self):
        config = AppConfig()
        engine = VisionEngine(config)
        # Create a scene with a known pattern
        scene = np.zeros((200, 300, 3), dtype=np.uint8)
        scene[50:80, 100:150] = 255  # White rectangle
        template = np.ones((30, 50, 3), dtype=np.uint8) * 255  # White template
        result = engine.find_template(scene, template)
        assert result is not None
        x, y, confidence = result
        # Template is 50x30, placed at (100,50), so center = (125, 65)
        assert 120 <= x <= 130
        assert 60 <= y <= 70
        assert confidence > 0.8

    def test_find_template_returns_none_when_not_found(self):
        config = AppConfig()
        engine = VisionEngine(config)
        scene = np.zeros((200, 300, 3), dtype=np.uint8)
        template = np.ones((30, 50, 3), dtype=np.uint8) * 255
        result = engine.find_template(scene, template)
        assert result is None

    def test_find_template_grayscale_fallback(self):
        config = AppConfig()
        engine = VisionEngine(config)
        # Slightly different color but same shape
        scene = np.zeros((200, 300, 3), dtype=np.uint8)
        scene[50:80, 100:150] = [250, 250, 250]
        template = np.ones((30, 50, 3), dtype=np.uint8) * 255
        result = engine.find_template(scene, template)
        assert result is not None


class TestOCR:
    def test_find_text_returns_location(self):
        config = AppConfig()
        engine = VisionEngine(config)
        mock_ocr = MagicMock()
        mock_ocr.ocr.return_value = [
            [
                [
                    [[100, 50], [200, 50], [200, 80], [100, 80]],
                    ("確認", 0.95),
                ]
            ]
        ]
        engine._ocr = mock_ocr
        scene = np.zeros((200, 300, 3), dtype=np.uint8)
        result = engine.find_text(scene, "確認")
        assert result is not None
        x, y, confidence = result
        assert x == 150  # center x
        assert y == 65  # center y
        assert confidence == 0.95

    def test_find_text_returns_none_when_not_found(self):
        config = AppConfig()
        engine = VisionEngine(config)
        mock_ocr = MagicMock()
        mock_ocr.ocr.return_value = [
            [
                [
                    [[100, 50], [200, 50], [200, 80], [100, 80]],
                    ("取消", 0.90),
                ]
            ]
        ]
        engine._ocr = mock_ocr
        scene = np.zeros((200, 300, 3), dtype=np.uint8)
        result = engine.find_text(scene, "確認")
        assert result is None


class TestFallback:
    def test_find_element_tries_ocr_then_template(self):
        config = AppConfig()
        engine = VisionEngine(config)
        scene = np.zeros((200, 300, 3), dtype=np.uint8)
        template = np.ones((30, 50, 3), dtype=np.uint8) * 255
        # OCR fails, template succeeds
        mock_ocr = MagicMock()
        mock_ocr.ocr.return_value = [[]]
        engine._ocr = mock_ocr
        scene[50:80, 100:150] = 255
        result = engine.find_element(
            scene, text="確認", template=template
        )
        assert result is not None
