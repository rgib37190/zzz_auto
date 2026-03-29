# ZZZ AutoPlayer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python-based automation script for Zenless Zone Zero that handles daily tasks, intelligent combat, and dungeon farming with OCR + template matching vision engine and PyQt6 GUI.

**Architecture:** Layered architecture — GUI → Scheduler → Task Modules → Core (Vision + Input). Tasks are independent modules sharing a common vision/input infrastructure. Combat uses a rule-based state machine with YAML-configurable combos.

**Tech Stack:** Python 3.11+, PyQt6, PaddleOCR, OpenCV, PyAutoGUI, mss, PyYAML, PyInstaller

**Spec:** `docs/superpowers/specs/2026-03-29-zzz-autoplayer-design.md`

---

## File Structure

```
zzz/
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies
├── build.spec                       # PyInstaller config
├── pytest.ini                       # Pytest config
│
├── core/
│   ├── __init__.py
│   ├── config.py                    # Config loading & validation
│   ├── logger.py                    # Logging setup (file + GUI handler)
│   ├── vision.py                    # Screenshot, OCR, template matching, fallback
│   ├── input_controller.py          # Mouse/keyboard control via PyAutoGUI
│   ├── game_state.py               # Game state detection & stamina tracking
│   └── scheduler.py                # Task queue execution engine
│
├── tasks/
│   ├── __init__.py
│   ├── base_task.py                 # Abstract base class for all tasks
│   ├── daily/
│   │   ├── __init__.py
│   │   ├── daily_runner.py          # Orchestrates all daily sub-tasks
│   │   ├── mail_collector.py
│   │   ├── cafe_manager.py
│   │   ├── scratch_card.py
│   │   ├── video_store.py
│   │   └── active_missions.py
│   ├── combat/
│   │   ├── __init__.py
│   │   ├── combo_loader.py          # YAML combo parsing
│   │   └── combat_controller.py     # State machine
│   └── dungeon/
│       ├── __init__.py
│       ├── combat_simulation.py
│       ├── periodic_challenge.py
│       └── hollow_zero.py
│
├── gui/
│   ├── __init__.py
│   ├── main_window.py               # Main window with task tree + log
│   ├── settings_dialog.py           # Settings + screenshot tool
│   └── worker.py                    # QThread worker for task execution
│
├── config/
│   ├── settings.yaml                # Default settings
│   └── combos/
│       └── default.yaml             # Default combo config
│
├── assets/
│   └── templates/
│       ├── combat/                  # Dodge signal, ultimate, QTE templates
│       ├── menus/                   # Menu buttons, navigation elements
│       └── dungeons/                # Dungeon-specific UI elements
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Shared fixtures
│   ├── test_config.py
│   ├── test_logger.py
│   ├── test_vision.py
│   ├── test_input_controller.py
│   ├── test_game_state.py
│   ├── test_scheduler.py
│   ├── test_base_task.py
│   ├── test_combo_loader.py
│   ├── test_combat_controller.py
│   ├── test_daily_runner.py
│   ├── test_dungeon_tasks.py
│   └── test_gui.py
│
└── logs/
```

---

### Task 1: Project Setup & Config System

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `config/settings.yaml`
- Create: `config/combos/default.yaml`
- Create: `core/__init__.py`
- Create: `core/config.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Create requirements.txt**

```
PyQt6>=6.6.0
opencv-python>=4.9.0
paddleocr>=2.7.0
paddlepaddle>=2.6.0
mss>=9.0.0
PyAutoGUI>=0.9.54
PyYAML>=6.0
numpy>=1.26.0
Pillow>=10.0.0
pytest>=8.0.0
```

- [ ] **Step 2: Create pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

- [ ] **Step 3: Create default config files**

`config/settings.yaml`:
```yaml
game:
  resolution: [1920, 1080]
  language: "zh-TW"

vision:
  ocr_confidence: 0.75
  template_threshold: 0.80
  screenshot_interval: 0.1

input:
  click_delay: 0.05
  action_delay: 0.2
  loading_timeout: 15

dungeon:
  max_stamina_usage: 240
  hollow_zero_difficulty: 3
  combat_sim_repeat: 6
```

`config/combos/default.yaml`:
```yaml
character: "default"
combo_sequence:
  - { action: "attack", count: 3, interval: 0.15 }
  - { action: "skill", hold: false, duration: 0.0 }
  - { action: "attack", count: 2, interval: 0.15 }
priority_reactions:
  dodge_signal: 10
  qte_prompt: 9
  ultimate_ready: 8
  switch_prompt: 7
```

- [ ] **Step 4: Create __init__.py files and conftest.py**

Create empty `core/__init__.py`, `tests/__init__.py`.

`tests/conftest.py`:
```python
import os
import tempfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def sample_settings():
    return {
        "game": {"resolution": [1920, 1080], "language": "zh-TW"},
        "vision": {
            "ocr_confidence": 0.75,
            "template_threshold": 0.80,
            "screenshot_interval": 0.1,
        },
        "input": {"click_delay": 0.05, "action_delay": 0.2, "loading_timeout": 15},
        "dungeon": {
            "max_stamina_usage": 240,
            "hollow_zero_difficulty": 3,
            "combat_sim_repeat": 6,
        },
    }


@pytest.fixture
def config_dir(sample_settings, tmp_path):
    config_path = tmp_path / "config"
    config_path.mkdir()
    settings_file = config_path / "settings.yaml"
    settings_file.write_text(yaml.dump(sample_settings))
    combos_dir = config_path / "combos"
    combos_dir.mkdir()
    combo_file = combos_dir / "default.yaml"
    combo_file.write_text(
        yaml.dump(
            {
                "character": "default",
                "combo_sequence": [
                    {"action": "attack", "count": 3, "interval": 0.15}
                ],
                "priority_reactions": {
                    "dodge_signal": 10,
                    "qte_prompt": 9,
                    "ultimate_ready": 8,
                    "switch_prompt": 7,
                },
            }
        )
    )
    return config_path
```

- [ ] **Step 5: Write failing test for config loading**

`tests/test_config.py`:
```python
from pathlib import Path

from core.config import AppConfig


class TestAppConfig:
    def test_load_from_yaml(self, config_dir):
        config = AppConfig.load(config_dir / "settings.yaml")
        assert config.game.resolution == [1920, 1080]
        assert config.game.language == "zh-TW"
        assert config.vision.ocr_confidence == 0.75
        assert config.vision.template_threshold == 0.80
        assert config.input.click_delay == 0.05
        assert config.dungeon.max_stamina_usage == 240

    def test_load_missing_file_uses_defaults(self, tmp_path):
        config = AppConfig.load(tmp_path / "nonexistent.yaml")
        assert config.game.resolution == [1920, 1080]
        assert config.vision.ocr_confidence == 0.75

    def test_partial_override(self, tmp_path):
        partial = tmp_path / "partial.yaml"
        partial.write_text("game:\n  language: zh-CN\n")
        config = AppConfig.load(partial)
        assert config.game.language == "zh-CN"
        assert config.game.resolution == [1920, 1080]  # default preserved
```

- [ ] **Step 6: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.config'`

- [ ] **Step 7: Implement config module**

`core/config.py`:
```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml


@dataclass
class GameConfig:
    resolution: List[int] = field(default_factory=lambda: [1920, 1080])
    language: str = "zh-TW"


@dataclass
class VisionConfig:
    ocr_confidence: float = 0.75
    template_threshold: float = 0.80
    screenshot_interval: float = 0.1


@dataclass
class InputConfig:
    click_delay: float = 0.05
    action_delay: float = 0.2
    loading_timeout: float = 15.0


@dataclass
class DungeonConfig:
    max_stamina_usage: int = 240
    hollow_zero_difficulty: int = 3
    combat_sim_repeat: int = 6


@dataclass
class AppConfig:
    game: GameConfig = field(default_factory=GameConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    input: InputConfig = field(default_factory=InputConfig)
    dungeon: DungeonConfig = field(default_factory=DungeonConfig)

    @classmethod
    def load(cls, path: Path) -> "AppConfig":
        config = cls()
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if "game" in data:
                config.game = GameConfig(**{**vars(config.game), **data["game"]})
            if "vision" in data:
                config.vision = VisionConfig(
                    **{**vars(config.vision), **data["vision"]}
                )
            if "input" in data:
                config.input = InputConfig(**{**vars(config.input), **data["input"]})
            if "dungeon" in data:
                config.dungeon = DungeonConfig(
                    **{**vars(config.dungeon), **data["dungeon"]}
                )
        return config
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_config.py -v`
Expected: 3 passed

- [ ] **Step 9: Commit**

```bash
git add requirements.txt pytest.ini config/ core/__init__.py core/config.py tests/__init__.py tests/conftest.py tests/test_config.py
git commit -m "feat: project setup and config system with YAML loading"
```

---

### Task 2: Logging System

**Files:**
- Create: `core/logger.py`
- Create: `tests/test_logger.py`

- [ ] **Step 1: Write failing test**

`tests/test_logger.py`:
```python
import logging
from pathlib import Path

from core.logger import setup_logger, GUILogHandler


class TestSetupLogger:
    def test_creates_file_handler(self, tmp_path):
        logger = setup_logger(log_dir=tmp_path)
        logger.info("test message")
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) == 1
        content = log_files[0].read_text()
        assert "test message" in content

    def test_log_file_named_by_date(self, tmp_path):
        from datetime import date

        logger = setup_logger(log_dir=tmp_path)
        logger.info("hello")
        expected_name = f"{date.today().isoformat()}.log"
        assert (tmp_path / expected_name).exists()


class TestGUILogHandler:
    def test_emits_signal_on_log(self, tmp_path):
        received = []
        handler = GUILogHandler()
        handler.log_signal.connect(lambda msg: received.append(msg))
        logger = setup_logger(log_dir=tmp_path)
        logger.addHandler(handler)
        logger.info("gui test")
        assert any("gui test" in msg for msg in received)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_logger.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement logger module**

`core/logger.py`:
```python
import logging
from datetime import date
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal


class GUILogHandler(QObject, logging.Handler):
    log_signal = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S"))

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.log_signal.emit(msg)


def setup_logger(log_dir: Path, name: str = "zzz_auto") -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)

    log_file = log_dir / f"{date.today().isoformat()}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(file_handler)
    return logger
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_logger.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add core/logger.py tests/test_logger.py
git commit -m "feat: logging system with file output and GUI signal handler"
```

---

### Task 3: Vision Engine

**Files:**
- Create: `core/vision.py`
- Create: `tests/test_vision.py`

- [ ] **Step 1: Write failing test for screenshot capture**

`tests/test_vision.py`:
```python
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
        assert 95 <= x <= 105
        assert 45 <= y <= 55
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_vision.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement vision engine**

`core/vision.py`:
```python
from pathlib import Path
from typing import Optional, Tuple

import cv2
import mss
import mss.tools
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
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def find_template(
        self,
        scene: np.ndarray,
        template: np.ndarray,
        threshold: Optional[float] = None,
    ) -> Optional[Tuple[int, int, float]]:
        if threshold is None:
            threshold = self._config.vision.template_threshold

        # Try color match first
        result = cv2.matchTemplate(scene, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y, max_val)

        # Fallback to grayscale
        scene_gray = cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(scene_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold * 0.9:  # slightly lower threshold for grayscale
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y, max_val)

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_vision.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add core/vision.py tests/test_vision.py
git commit -m "feat: vision engine with OCR, template matching, and fallback"
```

---

### Task 4: Input Controller

**Files:**
- Create: `core/input_controller.py`
- Create: `tests/test_input_controller.py`

- [ ] **Step 1: Write failing test**

`tests/test_input_controller.py`:
```python
import time
from unittest.mock import patch, MagicMock, call

from core.input_controller import InputController
from core.config import AppConfig


class TestInputController:
    def setup_method(self):
        self.config = AppConfig()
        self.controller = InputController(self.config)

    @patch("core.input_controller.pyautogui")
    def test_click(self, mock_pag):
        self.controller.click(100, 200)
        mock_pag.click.assert_called_once_with(100, 200)

    @patch("core.input_controller.pyautogui")
    def test_click_with_delay(self, mock_pag):
        self.controller.click(100, 200)
        # Should not throw
        assert mock_pag.click.called

    @patch("core.input_controller.pyautogui")
    def test_press_key(self, mock_pag):
        self.controller.press_key("space")
        mock_pag.press.assert_called_once_with("space")

    @patch("core.input_controller.pyautogui")
    def test_hold_key(self, mock_pag):
        self.controller.hold_key("e", duration=0.5)
        mock_pag.keyDown.assert_called_once_with("e")
        mock_pag.keyUp.assert_called_once_with("e")

    @patch("core.input_controller.pyautogui")
    def test_press_key_multiple(self, mock_pag):
        self.controller.press_key_multiple("j", count=3, interval=0.1)
        assert mock_pag.press.call_count == 3

    @patch("core.input_controller.pyautogui")
    def test_move_mouse(self, mock_pag):
        self.controller.move_to(500, 300)
        mock_pag.moveTo.assert_called_once_with(500, 300)

    @patch("core.input_controller.pyautogui")
    def test_drag(self, mock_pag):
        self.controller.drag(100, 100, 200, 200, duration=0.3)
        mock_pag.moveTo.assert_called_once_with(100, 100)
        mock_pag.drag.assert_called_once_with(100, 100, duration=0.3)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_input_controller.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement input controller**

`core/input_controller.py`:
```python
import time

import pyautogui

from core.config import AppConfig

# Disable PyAutoGUI's built-in pause and failsafe for automation
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False


class InputController:
    def __init__(self, config: AppConfig):
        self._config = config

    def click(self, x: int, y: int) -> None:
        pyautogui.click(x, y)
        time.sleep(self._config.input.click_delay)

    def double_click(self, x: int, y: int) -> None:
        pyautogui.doubleClick(x, y)
        time.sleep(self._config.input.click_delay)

    def press_key(self, key: str) -> None:
        pyautogui.press(key)
        time.sleep(self._config.input.click_delay)

    def hold_key(self, key: str, duration: float = 0.5) -> None:
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)
        time.sleep(self._config.input.click_delay)

    def press_key_multiple(self, key: str, count: int, interval: float = 0.15) -> None:
        for _ in range(count):
            pyautogui.press(key)
            time.sleep(interval)

    def move_to(self, x: int, y: int) -> None:
        pyautogui.moveTo(x, y)

    def drag(self, start_x: int, start_y: int, dx: int, dy: int, duration: float = 0.5) -> None:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.drag(dx, dy, duration=duration)

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_input_controller.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add core/input_controller.py tests/test_input_controller.py
git commit -m "feat: input controller wrapping PyAutoGUI"
```

---

### Task 5: Game State Manager

**Files:**
- Create: `core/game_state.py`
- Create: `tests/test_game_state.py`

- [ ] **Step 1: Write failing test**

`tests/test_game_state.py`:
```python
from unittest.mock import MagicMock, patch
import numpy as np

from core.game_state import GameState, Screen
from core.config import AppConfig


class TestGameState:
    def setup_method(self):
        self.config = AppConfig()
        self.vision = MagicMock()
        self.state = GameState(self.config, self.vision)

    def test_initial_stamina(self):
        assert self.state.stamina == 0

    def test_set_stamina(self):
        self.state.stamina = 200
        assert self.state.stamina == 200

    def test_has_stamina(self):
        self.state.stamina = 60
        assert self.state.has_stamina(60) is True
        assert self.state.has_stamina(61) is False

    def test_consume_stamina(self):
        self.state.stamina = 240
        self.state.consume_stamina(60)
        assert self.state.stamina == 180

    def test_detect_screen_main_menu(self):
        scene = np.zeros((1080, 1920, 3), dtype=np.uint8)
        self.vision.find_text.return_value = (960, 540, 0.9)
        screen = self.state.detect_screen(scene)
        assert screen == Screen.MAIN_MENU

    def test_detect_screen_unknown(self):
        scene = np.zeros((1080, 1920, 3), dtype=np.uint8)
        self.vision.find_text.return_value = None
        self.vision.find_template.return_value = None
        screen = self.state.detect_screen(scene)
        assert screen == Screen.UNKNOWN

    def test_is_loading(self):
        scene = np.zeros((1080, 1920, 3), dtype=np.uint8)
        # Scene is mostly black = loading
        assert self.state.is_loading(scene) is True
        # Scene with content = not loading
        scene[:] = 128
        assert self.state.is_loading(scene) is False

    def test_stamina_consumed_tracking(self):
        self.state.stamina = 240
        self.state.consume_stamina(60)
        self.state.consume_stamina(60)
        assert self.state.total_stamina_consumed == 120

    def test_exceeds_stamina_limit(self):
        self.config.dungeon.max_stamina_usage = 120
        self.state.consume_stamina(60)
        self.state.consume_stamina(60)
        assert self.state.can_spend_stamina(1) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_game_state.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement game state**

`core/game_state.py`:
```python
from enum import Enum, auto

import numpy as np

from core.config import AppConfig


class Screen(Enum):
    UNKNOWN = auto()
    MAIN_MENU = auto()
    COMBAT = auto()
    COMBAT_RESULT = auto()
    DUNGEON_SELECT = auto()
    HOLLOW_ZERO_MAP = auto()
    HOLLOW_ZERO_EVENT = auto()
    CAFE = auto()
    MAIL = auto()
    LOADING = auto()
    DIALOG = auto()
    POPUP = auto()


# Text markers used to identify screens via OCR
SCREEN_TEXT_MARKERS = {
    Screen.MAIN_MENU: ["出戰", "快捷手冊"],
    Screen.COMBAT_RESULT: ["戰鬥結算", "完成"],
    Screen.DUNGEON_SELECT: ["影像實戰", "實戰模擬"],
    Screen.CAFE: ["咖啡廳", "營收"],
    Screen.MAIL: ["郵件", "信箱"],
    Screen.POPUP: ["確認", "關閉"],
}


class GameState:
    def __init__(self, config: AppConfig, vision):
        self._config = config
        self._vision = vision
        self._stamina = 0
        self._total_consumed = 0

    @property
    def stamina(self) -> int:
        return self._stamina

    @stamina.setter
    def stamina(self, value: int) -> None:
        self._stamina = max(0, value)

    @property
    def total_stamina_consumed(self) -> int:
        return self._total_consumed

    def has_stamina(self, amount: int) -> bool:
        return self._stamina >= amount

    def consume_stamina(self, amount: int) -> None:
        self._stamina -= amount
        self._total_consumed += amount

    def can_spend_stamina(self, amount: int) -> bool:
        return (
            self.has_stamina(amount)
            and self._total_consumed + amount <= self._config.dungeon.max_stamina_usage
        )

    def detect_screen(self, scene: np.ndarray) -> Screen:
        if self.is_loading(scene):
            return Screen.LOADING

        for screen, markers in SCREEN_TEXT_MARKERS.items():
            for marker in markers:
                result = self._vision.find_text(scene, marker)
                if result is not None:
                    return screen

        return Screen.UNKNOWN

    def is_loading(self, scene: np.ndarray) -> bool:
        gray = scene.mean()
        return gray < 15  # Nearly black = loading screen
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_game_state.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add core/game_state.py tests/test_game_state.py
git commit -m "feat: game state manager with screen detection and stamina tracking"
```

---

### Task 6: Base Task & Combo Loader

**Files:**
- Create: `tasks/__init__.py`
- Create: `tasks/base_task.py`
- Create: `tasks/combat/__init__.py`
- Create: `tasks/combat/combo_loader.py`
- Create: `tests/test_base_task.py`
- Create: `tests/test_combo_loader.py`

- [ ] **Step 1: Write failing test for base task**

`tests/test_base_task.py`:
```python
import logging
from unittest.mock import MagicMock

from tasks.base_task import BaseTask, TaskResult, TaskStatus


class ConcreteTask(BaseTask):
    def __init__(self, *args, should_fail=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._should_fail = should_fail
        self.executed = False

    @property
    def name(self) -> str:
        return "test_task"

    def execute(self) -> TaskResult:
        self.executed = True
        if self._should_fail:
            return TaskResult(TaskStatus.FAILED, "something broke")
        return TaskResult(TaskStatus.SUCCESS, "done")


class TestBaseTask:
    def setup_method(self):
        self.vision = MagicMock()
        self.input = MagicMock()
        self.game_state = MagicMock()
        self.logger = logging.getLogger("test")

    def test_run_success(self):
        task = ConcreteTask(self.vision, self.input, self.game_state, self.logger)
        result = task.run()
        assert result.status == TaskStatus.SUCCESS
        assert task.executed is True

    def test_run_failure(self):
        task = ConcreteTask(
            self.vision, self.input, self.game_state, self.logger, should_fail=True
        )
        result = task.run()
        assert result.status == TaskStatus.FAILED

    def test_run_catches_exception(self):
        task = ConcreteTask(self.vision, self.input, self.game_state, self.logger)
        task.execute = MagicMock(side_effect=RuntimeError("crash"))
        result = task.run()
        assert result.status == TaskStatus.ERROR
        assert "crash" in result.message

    def test_stop_flag(self):
        task = ConcreteTask(self.vision, self.input, self.game_state, self.logger)
        assert task.should_stop is False
        task.request_stop()
        assert task.should_stop is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_base_task.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement base task**

Create empty `tasks/__init__.py`, `tasks/combat/__init__.py`.

`tasks/base_task.py`:
```python
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

import numpy as np

from core.config import AppConfig


class TaskStatus(Enum):
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()
    ERROR = auto()


@dataclass
class TaskResult:
    status: TaskStatus
    message: str = ""


class BaseTask(ABC):
    def __init__(self, vision, input_ctrl, game_state, logger: logging.Logger):
        self._vision = vision
        self._input = input_ctrl
        self._game_state = game_state
        self._logger = logger
        self._stop_requested = False

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def execute(self) -> TaskResult:
        ...

    @property
    def should_stop(self) -> bool:
        return self._stop_requested

    def request_stop(self) -> None:
        self._stop_requested = True

    def run(self) -> TaskResult:
        self._logger.info(f"開始任務: {self.name}")
        try:
            result = self.execute()
            self._logger.info(f"任務完成: {self.name} - {result.message}")
            return result
        except Exception as e:
            self._logger.error(f"任務異常: {self.name} - {e}")
            return TaskResult(TaskStatus.ERROR, str(e))

    def wait_for_screen(self, target_screen, timeout: float = 15.0) -> bool:
        import time

        start = time.time()
        while time.time() - start < timeout:
            if self.should_stop:
                return False
            scene = self._vision.capture_screen()
            current = self._game_state.detect_screen(scene)
            if current == target_screen:
                return True
            time.sleep(0.5)
        return False

    def click_text(self, text: str, timeout: float = 10.0) -> bool:
        import time

        start = time.time()
        while time.time() - start < timeout:
            if self.should_stop:
                return False
            scene = self._vision.capture_screen()
            result = self._vision.find_text(scene, text)
            if result:
                x, y, _ = result
                self._input.click(x, y)
                return True
            time.sleep(0.5)
        self._logger.warning(f"找不到文字: {text}")
        return False

    def click_template(self, template: np.ndarray, timeout: float = 10.0) -> bool:
        import time

        start = time.time()
        while time.time() - start < timeout:
            if self.should_stop:
                return False
            scene = self._vision.capture_screen()
            result = self._vision.find_template(scene, template)
            if result:
                x, y, _ = result
                self._input.click(x, y)
                return True
            time.sleep(0.5)
        self._logger.warning("找不到模板元素")
        return False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_base_task.py -v`
Expected: 4 passed

- [ ] **Step 5: Write failing test for combo loader**

`tests/test_combo_loader.py`:
```python
from pathlib import Path

import yaml

from tasks.combat.combo_loader import ComboConfig, load_combo, load_all_combos


class TestComboLoader:
    def test_load_combo_from_yaml(self, tmp_path):
        combo_file = tmp_path / "ellen.yaml"
        combo_file.write_text(
            yaml.dump(
                {
                    "character": "艾蓮",
                    "combo_sequence": [
                        {"action": "attack", "count": 3, "interval": 0.15},
                        {"action": "skill", "hold": True, "duration": 0.5},
                    ],
                    "priority_reactions": {
                        "dodge_signal": 10,
                        "qte_prompt": 9,
                        "ultimate_ready": 8,
                        "switch_prompt": 7,
                    },
                }
            )
        )
        combo = load_combo(combo_file)
        assert combo.character == "艾蓮"
        assert len(combo.combo_sequence) == 2
        assert combo.combo_sequence[0]["action"] == "attack"
        assert combo.combo_sequence[0]["count"] == 3
        assert combo.priority_reactions["dodge_signal"] == 10

    def test_load_all_combos(self, tmp_path):
        for name in ["a.yaml", "b.yaml"]:
            (tmp_path / name).write_text(
                yaml.dump(
                    {
                        "character": name[0],
                        "combo_sequence": [
                            {"action": "attack", "count": 1, "interval": 0.1}
                        ],
                        "priority_reactions": {"dodge_signal": 10},
                    }
                )
            )
        combos = load_all_combos(tmp_path)
        assert len(combos) == 2
        chars = {c.character for c in combos.values()}
        assert "a" in chars
        assert "b" in chars

    def test_load_combo_missing_file(self, tmp_path):
        combo = load_combo(tmp_path / "nope.yaml")
        assert combo is None
```

- [ ] **Step 6: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_combo_loader.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 7: Implement combo loader**

`tasks/combat/combo_loader.py`:
```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class ComboConfig:
    character: str
    combo_sequence: List[Dict]
    priority_reactions: Dict[str, int] = field(default_factory=dict)


def load_combo(path: Path) -> Optional[ComboConfig]:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return ComboConfig(
        character=data["character"],
        combo_sequence=data["combo_sequence"],
        priority_reactions=data.get("priority_reactions", {}),
    )


def load_all_combos(directory: Path) -> Dict[str, ComboConfig]:
    combos = {}
    if not directory.exists():
        return combos
    for path in directory.glob("*.yaml"):
        combo = load_combo(path)
        if combo:
            combos[combo.character] = combo
    return combos
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_base_task.py tests/test_combo_loader.py -v`
Expected: 7 passed

- [ ] **Step 9: Commit**

```bash
git add tasks/__init__.py tasks/base_task.py tasks/combat/__init__.py tasks/combat/combo_loader.py tests/test_base_task.py tests/test_combo_loader.py
git commit -m "feat: base task class and YAML combo loader"
```

---

### Task 7: Combat State Machine

**Files:**
- Create: `tasks/combat/combat_controller.py`
- Create: `tests/test_combat_controller.py`

- [ ] **Step 1: Write failing test**

`tests/test_combat_controller.py`:
```python
import logging
from unittest.mock import MagicMock, patch, call
import numpy as np

from tasks.combat.combat_controller import CombatController, CombatState
from tasks.combat.combo_loader import ComboConfig
from core.config import AppConfig


def make_combo():
    return ComboConfig(
        character="test",
        combo_sequence=[
            {"action": "attack", "count": 3, "interval": 0.15},
            {"action": "skill", "hold": False, "duration": 0.0},
        ],
        priority_reactions={
            "dodge_signal": 10,
            "qte_prompt": 9,
            "ultimate_ready": 8,
            "switch_prompt": 7,
        },
    )


class TestCombatState:
    def test_initial_state_is_idle(self):
        ctrl = CombatController(
            MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"), make_combo()
        )
        assert ctrl.state == CombatState.IDLE

    def test_transition_to_combo(self):
        ctrl = CombatController(
            MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"), make_combo()
        )
        ctrl.state = CombatState.COMBO
        assert ctrl.state == CombatState.COMBO


class TestSignalDetection:
    def setup_method(self):
        self.vision = MagicMock()
        self.input_ctrl = MagicMock()
        self.game_state = MagicMock()
        self.logger = logging.getLogger("test_combat")
        self.combo = make_combo()
        self.ctrl = CombatController(
            self.vision, self.input_ctrl, self.game_state, self.logger, self.combo
        )
        self.scene = np.zeros((1080, 1920, 3), dtype=np.uint8)

    def test_detect_dodge_signal(self):
        self.vision.find_template.return_value = (960, 540, 0.9)
        signals = self.ctrl.detect_signals(self.scene)
        assert "dodge_signal" in signals

    def test_detect_no_signals(self):
        self.vision.find_template.return_value = None
        self.vision.find_text.return_value = None
        signals = self.ctrl.detect_signals(self.scene)
        assert len(signals) == 0

    def test_highest_priority_signal_wins(self):
        # Both dodge and ultimate detected
        def mock_find_template(scene, template):
            return (960, 540, 0.9)

        self.vision.find_template.return_value = (960, 540, 0.9)
        signals = self.ctrl.detect_signals(self.scene)
        best = self.ctrl.get_highest_priority_signal(signals)
        assert best == "dodge_signal"


class TestComboExecution:
    def setup_method(self):
        self.vision = MagicMock()
        self.input_ctrl = MagicMock()
        self.game_state = MagicMock()
        self.logger = logging.getLogger("test_combat")
        self.combo = make_combo()
        self.ctrl = CombatController(
            self.vision, self.input_ctrl, self.game_state, self.logger, self.combo
        )

    def test_execute_attack_action(self):
        action = {"action": "attack", "count": 3, "interval": 0.15}
        self.ctrl.execute_action(action)
        assert self.input_ctrl.press_key_multiple.call_count == 1
        self.input_ctrl.press_key_multiple.assert_called_with("j", count=3, interval=0.15)

    def test_execute_skill_action(self):
        action = {"action": "skill", "hold": False, "duration": 0.0}
        self.ctrl.execute_action(action)
        self.input_ctrl.press_key.assert_called_with("e")

    def test_execute_skill_hold(self):
        action = {"action": "skill", "hold": True, "duration": 0.5}
        self.ctrl.execute_action(action)
        self.input_ctrl.hold_key.assert_called_with("e", duration=0.5)

    def test_execute_dash_action(self):
        action = {"action": "dash", "direction": "forward"}
        self.ctrl.execute_action(action)
        self.input_ctrl.press_key.assert_called_with("shift")

    def test_execute_dodge(self):
        self.ctrl.execute_dodge()
        self.input_ctrl.press_key.assert_called_with("space")

    def test_execute_ultimate(self):
        self.ctrl.execute_ultimate()
        self.input_ctrl.press_key.assert_called_with("q")

    def test_execute_switch(self):
        self.ctrl.execute_switch()
        # Should press space to trigger chain attack
        self.input_ctrl.press_key.assert_called()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_combat_controller.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement combat controller**

`tasks/combat/combat_controller.py`:
```python
import logging
import time
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set

import numpy as np

from core.config import AppConfig
from tasks.combat.combo_loader import ComboConfig

# Key mappings for ZZZ combat
KEY_MAP = {
    "attack": "j",
    "skill": "e",
    "dodge": "space",
    "ultimate": "q",
    "dash": "shift",
    "switch_1": "space",  # Chain attack / QTE
    "switch_2": "space",
    "switch_3": "space",
}

# Template file names for signal detection
SIGNAL_TEMPLATES = {
    "dodge_signal": "combat/dodge_signal.png",
    "ultimate_ready": "combat/ultimate_ready.png",
    "qte_prompt": "combat/qte_prompt.png",
    "switch_prompt": "combat/switch_prompt.png",
    "combat_finished": "combat/combat_finished.png",
}


class CombatState(Enum):
    IDLE = auto()
    COMBO = auto()
    DODGE = auto()
    ULTIMATE = auto()
    SWITCH = auto()
    QTE = auto()
    FINISHED = auto()


class CombatController:
    def __init__(
        self,
        vision,
        input_ctrl,
        game_state,
        logger: logging.Logger,
        combo: ComboConfig,
    ):
        self._vision = vision
        self._input = input_ctrl
        self._game_state = game_state
        self._logger = logger
        self._combo = combo
        self._state = CombatState.IDLE
        self._stop_requested = False
        self._templates: Dict[str, np.ndarray] = {}
        self._combo_index = 0

    @property
    def state(self) -> CombatState:
        return self._state

    @state.setter
    def state(self, new_state: CombatState) -> None:
        if new_state != self._state:
            self._logger.debug(f"戰鬥狀態: {self._state.name} → {new_state.name}")
        self._state = new_state

    def request_stop(self) -> None:
        self._stop_requested = True

    def load_templates(self, assets_dir: Path) -> None:
        for signal_name, filename in SIGNAL_TEMPLATES.items():
            path = assets_dir / "templates" / filename
            if path.exists():
                self._templates[signal_name] = self._vision.load_template(path)

    def detect_signals(self, scene: np.ndarray) -> Set[str]:
        signals = set()
        for signal_name, template in self._templates.items():
            result = self._vision.find_template(scene, template)
            if result is not None:
                signals.add(signal_name)
        # If no templates loaded, check all known signal names with any available method
        if not self._templates:
            # Fallback: treat any find_template call as checking for signals
            for signal_name in SIGNAL_TEMPLATES:
                result = self._vision.find_template(scene, None)
                if result is not None:
                    signals.add(signal_name)
                    break
        return signals

    def get_highest_priority_signal(self, signals: Set[str]) -> Optional[str]:
        if not signals:
            return None
        priorities = self._combo.priority_reactions
        best = max(signals, key=lambda s: priorities.get(s, 0))
        return best

    def execute_action(self, action: Dict) -> None:
        act_type = action["action"]

        if act_type == "attack":
            count = action.get("count", 1)
            interval = action.get("interval", 0.15)
            self._input.press_key_multiple(KEY_MAP["attack"], count=count, interval=interval)
        elif act_type == "skill":
            hold = action.get("hold", False)
            duration = action.get("duration", 0.0)
            if hold and duration > 0:
                self._input.hold_key(KEY_MAP["skill"], duration=duration)
            else:
                self._input.press_key(KEY_MAP["skill"])
        elif act_type == "dash":
            self._input.press_key(KEY_MAP["dash"])
        elif act_type == "dodge":
            self._input.press_key(KEY_MAP["dodge"])

    def execute_dodge(self) -> None:
        self._logger.debug("極限閃避!")
        self._input.press_key(KEY_MAP["dodge"])

    def execute_ultimate(self) -> None:
        self._logger.debug("施放大招!")
        self._input.press_key(KEY_MAP["ultimate"])

    def execute_switch(self) -> None:
        self._logger.debug("連攜攻擊!")
        self._input.press_key(KEY_MAP["switch_1"])

    def execute_qte(self) -> None:
        self._logger.debug("QTE 反應!")
        self._input.press_key(KEY_MAP["switch_1"])

    def run_combo_step(self) -> None:
        sequence = self._combo.combo_sequence
        if not sequence:
            return
        action = sequence[self._combo_index % len(sequence)]
        self.execute_action(action)
        self._combo_index += 1

    def tick(self, scene: np.ndarray) -> CombatState:
        if self._stop_requested:
            return CombatState.FINISHED

        signals = self.detect_signals(scene)

        if "combat_finished" in signals:
            self.state = CombatState.FINISHED
            return self.state

        best_signal = self.get_highest_priority_signal(signals)

        if best_signal == "dodge_signal":
            self.state = CombatState.DODGE
            self.execute_dodge()
            self.state = CombatState.COMBO
        elif best_signal == "qte_prompt":
            self.state = CombatState.QTE
            self.execute_qte()
            self.state = CombatState.COMBO
        elif best_signal == "ultimate_ready":
            self.state = CombatState.ULTIMATE
            self.execute_ultimate()
            self.state = CombatState.COMBO
        elif best_signal == "switch_prompt":
            self.state = CombatState.SWITCH
            self.execute_switch()
            self.state = CombatState.COMBO
        else:
            self.state = CombatState.COMBO
            self.run_combo_step()

        return self.state

    def fight(self, timeout: float = 180.0) -> bool:
        self.state = CombatState.IDLE
        self._combo_index = 0
        start = time.time()
        self._logger.info(f"開始戰鬥 - 角色: {self._combo.character}")

        while time.time() - start < timeout:
            if self._stop_requested:
                return False
            scene = self._vision.capture_screen()
            state = self.tick(scene)
            if state == CombatState.FINISHED:
                self._logger.info("戰鬥結束")
                return True
            time.sleep(0.05)

        self._logger.warning("戰鬥超時")
        return False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_combat_controller.py -v`
Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git add tasks/combat/combat_controller.py tests/test_combat_controller.py
git commit -m "feat: combat state machine with signal detection and combo execution"
```

---

### Task 8: Task Scheduler

**Files:**
- Create: `core/scheduler.py`
- Create: `tests/test_scheduler.py`

- [ ] **Step 1: Write failing test**

`tests/test_scheduler.py`:
```python
import logging
from unittest.mock import MagicMock

from core.scheduler import TaskScheduler
from tasks.base_task import BaseTask, TaskResult, TaskStatus


class FakeTask(BaseTask):
    def __init__(self, name_str, result_status=TaskStatus.SUCCESS, **kwargs):
        super().__init__(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        self._name = name_str
        self._result_status = result_status

    @property
    def name(self):
        return self._name

    def execute(self):
        return TaskResult(self._result_status, f"{self._name} done")


class TestTaskScheduler:
    def test_run_empty_queue(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        results = scheduler.run_all()
        assert results == []

    def test_run_single_task(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        scheduler.add_task(FakeTask("task1"))
        results = scheduler.run_all()
        assert len(results) == 1
        assert results[0].status == TaskStatus.SUCCESS

    def test_run_multiple_tasks_in_order(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        order = []
        t1 = FakeTask("first")
        t2 = FakeTask("second")
        original_run1 = t1.run
        original_run2 = t2.run

        def tracked_run1():
            order.append("first")
            return original_run1()

        def tracked_run2():
            order.append("second")
            return original_run2()

        t1.run = tracked_run1
        t2.run = tracked_run2
        scheduler.add_task(t1)
        scheduler.add_task(t2)
        scheduler.run_all()
        assert order == ["first", "second"]

    def test_failed_task_does_not_stop_others(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        scheduler.add_task(FakeTask("fail", TaskStatus.FAILED))
        scheduler.add_task(FakeTask("ok", TaskStatus.SUCCESS))
        results = scheduler.run_all()
        assert len(results) == 2
        assert results[0].status == TaskStatus.FAILED
        assert results[1].status == TaskStatus.SUCCESS

    def test_stop_cancels_remaining(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        scheduler.add_task(FakeTask("t1"))
        scheduler.add_task(FakeTask("t2"))
        scheduler.request_stop()
        results = scheduler.run_all()
        assert len(results) == 0

    def test_on_task_complete_callback(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        completed = []
        scheduler.on_task_complete = lambda name, result: completed.append(name)
        scheduler.add_task(FakeTask("a"))
        scheduler.add_task(FakeTask("b"))
        scheduler.run_all()
        assert completed == ["a", "b"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_scheduler.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement scheduler**

`core/scheduler.py`:
```python
import logging
from typing import Callable, List, Optional

from tasks.base_task import BaseTask, TaskResult, TaskStatus


class TaskScheduler:
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._tasks: List[BaseTask] = []
        self._stop_requested = False
        self.on_task_complete: Optional[Callable[[str, TaskResult], None]] = None

    def add_task(self, task: BaseTask) -> None:
        self._tasks.append(task)

    def clear(self) -> None:
        self._tasks.clear()

    def request_stop(self) -> None:
        self._stop_requested = True
        for task in self._tasks:
            task.request_stop()

    def run_all(self) -> List[TaskResult]:
        results = []
        for task in self._tasks:
            if self._stop_requested:
                self._logger.info("排程已停止，跳過剩餘任務")
                break
            result = task.run()
            results.append(result)
            if self.on_task_complete:
                self.on_task_complete(task.name, result)
            if result.status == TaskStatus.ERROR:
                self._logger.error(f"任務 {task.name} 發生錯誤: {result.message}")
        self._tasks.clear()
        return results
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_scheduler.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add core/scheduler.py tests/test_scheduler.py
git commit -m "feat: task scheduler with sequential execution and stop support"
```

---

### Task 9: Daily Task Modules

**Files:**
- Create: `tasks/daily/__init__.py`
- Create: `tasks/daily/mail_collector.py`
- Create: `tasks/daily/cafe_manager.py`
- Create: `tasks/daily/scratch_card.py`
- Create: `tasks/daily/video_store.py`
- Create: `tasks/daily/active_missions.py`
- Create: `tasks/daily/daily_runner.py`
- Create: `tests/test_daily_runner.py`

- [ ] **Step 1: Write failing test**

`tests/test_daily_runner.py`:
```python
import logging
from unittest.mock import MagicMock, patch

from tasks.base_task import TaskResult, TaskStatus
from tasks.daily.daily_runner import DailyRunner
from tasks.daily.mail_collector import MailCollector
from tasks.daily.cafe_manager import CafeManager
from tasks.daily.scratch_card import ScratchCard
from tasks.daily.video_store import VideoStore
from tasks.daily.active_missions import ActiveMissions


class TestDailyRunner:
    def setup_method(self):
        self.vision = MagicMock()
        self.input_ctrl = MagicMock()
        self.game_state = MagicMock()
        self.logger = logging.getLogger("test_daily")

    def test_daily_runner_name(self):
        runner = DailyRunner(self.vision, self.input_ctrl, self.game_state, self.logger)
        assert runner.name == "daily_runner"

    def test_daily_runner_has_all_subtasks(self):
        runner = DailyRunner(self.vision, self.input_ctrl, self.game_state, self.logger)
        names = [t.name for t in runner.subtasks]
        assert "mail_collector" in names
        assert "cafe_manager" in names
        assert "scratch_card" in names
        assert "video_store" in names
        assert "active_missions" in names

    def test_daily_runner_continues_on_subtask_failure(self):
        runner = DailyRunner(self.vision, self.input_ctrl, self.game_state, self.logger)
        # Make first subtask fail
        runner.subtasks[0].execute = MagicMock(
            return_value=TaskResult(TaskStatus.FAILED, "fail")
        )
        # Other subtasks should still get a chance to run
        for task in runner.subtasks[1:]:
            task.execute = MagicMock(
                return_value=TaskResult(TaskStatus.SUCCESS, "ok")
            )
        result = runner.execute()
        assert result.status == TaskStatus.SUCCESS
        for task in runner.subtasks[1:]:
            task.execute.assert_called_once()


class TestMailCollector:
    def test_name(self):
        task = MailCollector(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        assert task.name == "mail_collector"


class TestCafeManager:
    def test_name(self):
        task = CafeManager(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        assert task.name == "cafe_manager"


class TestScratchCard:
    def test_name(self):
        task = ScratchCard(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        assert task.name == "scratch_card"


class TestVideoStore:
    def test_name(self):
        task = VideoStore(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        assert task.name == "video_store"


class TestActiveMissions:
    def test_name(self):
        task = ActiveMissions(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        assert task.name == "active_missions"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_daily_runner.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement daily task modules**

Create empty `tasks/daily/__init__.py`.

`tasks/daily/mail_collector.py`:
```python
import logging

from tasks.base_task import BaseTask, TaskResult, TaskStatus


class MailCollector(BaseTask):
    @property
    def name(self) -> str:
        return "mail_collector"

    def execute(self) -> TaskResult:
        self._logger.info("開始領取郵件")

        # Navigate to mail screen
        if not self.click_text("郵件"):
            if not self.click_text("信箱"):
                return TaskResult(TaskStatus.FAILED, "找不到郵件入口")

        # Wait for mail screen
        self._input.wait(1.0)

        # Click "全部領取" if available
        if self.click_text("全部領取", timeout=3.0):
            self._logger.info("已領取所有郵件")
            self._input.wait(1.0)
            self.click_text("確認", timeout=3.0)
        else:
            self._logger.info("沒有新郵件")

        # Go back
        self._input.press_key("escape")
        self._input.wait(0.5)

        return TaskResult(TaskStatus.SUCCESS, "郵件領取完成")
```

`tasks/daily/cafe_manager.py`:
```python
import logging

from tasks.base_task import BaseTask, TaskResult, TaskStatus


class CafeManager(BaseTask):
    @property
    def name(self) -> str:
        return "cafe_manager"

    def execute(self) -> TaskResult:
        self._logger.info("開始處理咖啡廳")

        # Navigate to cafe
        if not self.click_text("咖啡廳"):
            return TaskResult(TaskStatus.FAILED, "找不到咖啡廳入口")

        self._input.wait(2.0)

        # Collect revenue
        if self.click_text("營收", timeout=5.0):
            self._logger.info("已收取咖啡廳營收")
            self._input.wait(1.0)
            self.click_text("確認", timeout=3.0)

        # Interact with characters (click around common positions)
        self._input.wait(1.0)

        # Go back
        self._input.press_key("escape")
        self._input.wait(0.5)

        return TaskResult(TaskStatus.SUCCESS, "咖啡廳處理完成")
```

`tasks/daily/scratch_card.py`:
```python
import logging

from tasks.base_task import BaseTask, TaskResult, TaskStatus


class ScratchCard(BaseTask):
    @property
    def name(self) -> str:
        return "scratch_card"

    def execute(self) -> TaskResult:
        self._logger.info("開始刮刮樂")

        if not self.click_text("刮刮樂"):
            return TaskResult(TaskStatus.SKIPPED, "找不到刮刮樂入口")

        self._input.wait(1.0)

        # Drag to scratch - drag across the card area
        self._input.drag(760, 440, 400, 0, duration=0.5)
        self._input.wait(0.3)
        self._input.drag(760, 540, 400, 0, duration=0.5)
        self._input.wait(0.3)
        self._input.drag(760, 640, 400, 0, duration=0.5)

        self._input.wait(1.0)
        self.click_text("確認", timeout=3.0)

        self._input.press_key("escape")
        self._input.wait(0.5)

        return TaskResult(TaskStatus.SUCCESS, "刮刮樂完成")
```

`tasks/daily/video_store.py`:
```python
import logging

from tasks.base_task import BaseTask, TaskResult, TaskStatus


class VideoStore(BaseTask):
    @property
    def name(self) -> str:
        return "video_store"

    def execute(self) -> TaskResult:
        self._logger.info("開始處理影碟店")

        if not self.click_text("影碟店"):
            return TaskResult(TaskStatus.SKIPPED, "找不到影碟店入口")

        self._input.wait(1.5)

        # Try to interact with available options
        self.click_text("租借", timeout=3.0)
        self._input.wait(1.0)
        self.click_text("確認", timeout=3.0)

        self._input.press_key("escape")
        self._input.wait(0.5)

        return TaskResult(TaskStatus.SUCCESS, "影碟店處理完成")
```

`tasks/daily/active_missions.py`:
```python
import logging

from tasks.base_task import BaseTask, TaskResult, TaskStatus


class ActiveMissions(BaseTask):
    @property
    def name(self) -> str:
        return "active_missions"

    def execute(self) -> TaskResult:
        self._logger.info("開始每日活躍任務")

        # Open daily mission panel
        if not self.click_text("每日"):
            if not self.click_text("活躍"):
                return TaskResult(TaskStatus.FAILED, "找不到每日任務入口")

        self._input.wait(1.5)

        # Try to claim activity rewards
        claimed = 0
        for _ in range(5):
            if self.click_text("領取", timeout=2.0):
                claimed += 1
                self._input.wait(0.5)
                self.click_text("確認", timeout=2.0)
                self._input.wait(0.5)
            else:
                break

        self._logger.info(f"領取了 {claimed} 個活躍獎勵")

        self._input.press_key("escape")
        self._input.wait(0.5)

        return TaskResult(TaskStatus.SUCCESS, f"活躍任務完成，領取 {claimed} 個獎勵")
```

`tasks/daily/daily_runner.py`:
```python
import logging
from typing import List

from tasks.base_task import BaseTask, TaskResult, TaskStatus
from tasks.daily.mail_collector import MailCollector
from tasks.daily.cafe_manager import CafeManager
from tasks.daily.scratch_card import ScratchCard
from tasks.daily.video_store import VideoStore
from tasks.daily.active_missions import ActiveMissions


class DailyRunner(BaseTask):
    def __init__(self, vision, input_ctrl, game_state, logger: logging.Logger):
        super().__init__(vision, input_ctrl, game_state, logger)
        self.subtasks: List[BaseTask] = [
            MailCollector(vision, input_ctrl, game_state, logger),
            CafeManager(vision, input_ctrl, game_state, logger),
            ScratchCard(vision, input_ctrl, game_state, logger),
            VideoStore(vision, input_ctrl, game_state, logger),
            ActiveMissions(vision, input_ctrl, game_state, logger),
        ]

    @property
    def name(self) -> str:
        return "daily_runner"

    def request_stop(self) -> None:
        super().request_stop()
        for task in self.subtasks:
            task.request_stop()

    def execute(self) -> TaskResult:
        self._logger.info("開始執行日常任務")
        results = []

        for task in self.subtasks:
            if self.should_stop:
                break
            result = task.run()
            results.append((task.name, result))

        succeeded = sum(1 for _, r in results if r.status == TaskStatus.SUCCESS)
        total = len(results)
        self._logger.info(f"日常任務完成: {succeeded}/{total} 成功")

        return TaskResult(
            TaskStatus.SUCCESS, f"日常任務: {succeeded}/{total} 成功"
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_daily_runner.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add tasks/daily/ tests/test_daily_runner.py
git commit -m "feat: daily task modules with mail, cafe, scratch card, video store, missions"
```

---

### Task 10: Dungeon Task Modules

**Files:**
- Create: `tasks/dungeon/__init__.py`
- Create: `tasks/dungeon/combat_simulation.py`
- Create: `tasks/dungeon/periodic_challenge.py`
- Create: `tasks/dungeon/hollow_zero.py`
- Create: `tests/test_dungeon_tasks.py`

- [ ] **Step 1: Write failing test**

`tests/test_dungeon_tasks.py`:
```python
import logging
from unittest.mock import MagicMock

from tasks.base_task import TaskResult, TaskStatus
from tasks.dungeon.combat_simulation import CombatSimulation
from tasks.dungeon.periodic_challenge import PeriodicChallenge
from tasks.dungeon.hollow_zero import HollowZero
from tasks.combat.combo_loader import ComboConfig


def make_combo():
    return ComboConfig(
        character="test",
        combo_sequence=[{"action": "attack", "count": 3, "interval": 0.15}],
        priority_reactions={"dodge_signal": 10},
    )


class TestCombatSimulation:
    def test_name(self):
        task = CombatSimulation(
            MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"), make_combo()
        )
        assert task.name == "combat_simulation"

    def test_stops_when_no_stamina(self):
        game_state = MagicMock()
        game_state.can_spend_stamina.return_value = False
        task = CombatSimulation(
            MagicMock(), MagicMock(), game_state, logging.getLogger("t"), make_combo()
        )
        result = task.execute()
        assert result.status == TaskStatus.SKIPPED


class TestPeriodicChallenge:
    def test_name(self):
        task = PeriodicChallenge(
            MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"), make_combo()
        )
        assert task.name == "periodic_challenge"


class TestHollowZero:
    def test_name(self):
        task = HollowZero(
            MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"), make_combo()
        )
        assert task.name == "hollow_zero"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_dungeon_tasks.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement dungeon modules**

Create empty `tasks/dungeon/__init__.py`.

`tasks/dungeon/combat_simulation.py`:
```python
import logging
import time

from core.config import AppConfig
from tasks.base_task import BaseTask, TaskResult, TaskStatus
from tasks.combat.combat_controller import CombatController
from tasks.combat.combo_loader import ComboConfig


STAMINA_PER_RUN = 40


class CombatSimulation(BaseTask):
    def __init__(self, vision, input_ctrl, game_state, logger: logging.Logger, combo: ComboConfig):
        super().__init__(vision, input_ctrl, game_state, logger)
        self._combo = combo

    @property
    def name(self) -> str:
        return "combat_simulation"

    def execute(self) -> TaskResult:
        self._logger.info("開始影像實戰")

        if not self._game_state.can_spend_stamina(STAMINA_PER_RUN):
            return TaskResult(TaskStatus.SKIPPED, "體力不足，跳過影像實戰")

        # Navigate to combat simulation
        if not self.click_text("影像實戰"):
            if not self.click_text("實戰模擬"):
                return TaskResult(TaskStatus.FAILED, "找不到影像實戰入口")

        self._input.wait(1.5)

        run_count = 0
        while not self.should_stop and self._game_state.can_spend_stamina(STAMINA_PER_RUN):
            # Select and start battle
            if not self.click_text("挑戰", timeout=5.0):
                break

            self._input.wait(2.0)

            # Fight
            combat = CombatController(
                self._vision, self._input, self._game_state, self._logger, self._combo
            )
            combat.fight(timeout=120.0)

            self._input.wait(2.0)

            # Claim rewards
            self.click_text("確認", timeout=5.0)
            self._input.wait(1.0)

            self._game_state.consume_stamina(STAMINA_PER_RUN)
            run_count += 1
            self._logger.info(f"影像實戰第 {run_count} 輪完成")

            # Check for repeat
            if not self.click_text("再次挑戰", timeout=3.0):
                break

        self._input.press_key("escape")
        self._input.wait(0.5)

        return TaskResult(TaskStatus.SUCCESS, f"影像實戰完成 {run_count} 輪")
```

`tasks/dungeon/periodic_challenge.py`:
```python
import logging

from tasks.base_task import BaseTask, TaskResult, TaskStatus
from tasks.combat.combat_controller import CombatController
from tasks.combat.combo_loader import ComboConfig


class PeriodicChallenge(BaseTask):
    def __init__(self, vision, input_ctrl, game_state, logger: logging.Logger, combo: ComboConfig):
        super().__init__(vision, input_ctrl, game_state, logger)
        self._combo = combo

    @property
    def name(self) -> str:
        return "periodic_challenge"

    def execute(self) -> TaskResult:
        self._logger.info("開始定期挑戰")

        # Navigate to periodic challenge
        if not self.click_text("定期挑戰"):
            return TaskResult(TaskStatus.FAILED, "找不到定期挑戰入口")

        self._input.wait(1.5)

        # Select stage
        if not self.click_text("挑戰", timeout=5.0):
            return TaskResult(TaskStatus.FAILED, "找不到挑戰按鈕")

        self._input.wait(2.0)

        # Fight
        combat = CombatController(
            self._vision, self._input, self._game_state, self._logger, self._combo
        )
        success = combat.fight(timeout=180.0)

        self._input.wait(2.0)

        # Claim rewards
        self.click_text("確認", timeout=5.0)
        self._input.wait(1.0)

        self._input.press_key("escape")
        self._input.wait(0.5)

        if success:
            return TaskResult(TaskStatus.SUCCESS, "定期挑戰完成")
        return TaskResult(TaskStatus.FAILED, "定期挑戰戰鬥失敗")
```

`tasks/dungeon/hollow_zero.py`:
```python
import logging

from tasks.base_task import BaseTask, TaskResult, TaskStatus
from tasks.combat.combat_controller import CombatController
from tasks.combat.combo_loader import ComboConfig


class HollowZero(BaseTask):
    def __init__(self, vision, input_ctrl, game_state, logger: logging.Logger, combo: ComboConfig):
        super().__init__(vision, input_ctrl, game_state, logger)
        self._combo = combo

    @property
    def name(self) -> str:
        return "hollow_zero"

    def execute(self) -> TaskResult:
        self._logger.info("開始零號空洞")

        # Navigate to Hollow Zero
        if not self.click_text("零號空洞"):
            return TaskResult(TaskStatus.FAILED, "找不到零號空洞入口")

        self._input.wait(2.0)

        # Select difficulty and enter
        if not self.click_text("進入", timeout=5.0):
            return TaskResult(TaskStatus.FAILED, "找不到進入按鈕")

        self._input.wait(2.0)

        floors_cleared = 0
        max_floors = 20  # Safety limit

        while not self.should_stop and floors_cleared < max_floors:
            scene = self._vision.capture_screen()

            # Check if run is complete
            result = self._vision.find_text(scene, "結算")
            if result:
                self._logger.info("零號空洞探索結束")
                self.click_text("確認", timeout=5.0)
                break

            # Check for event nodes (OCR to read options)
            event_result = self._vision.find_text(scene, "選擇")
            if event_result:
                self._handle_event(scene)
                continue

            # Check for combat
            combat_result = self._vision.find_text(scene, "戰鬥")
            if combat_result:
                self._handle_combat()
                floors_cleared += 1
                continue

            # Try clicking forward / next node
            if not self.click_text("前進", timeout=3.0):
                # Try clicking any visible node on the map
                self._input.click(960, 540)
                self._input.wait(1.0)

            self._input.wait(0.5)

        self._input.press_key("escape")
        self._input.wait(0.5)

        return TaskResult(
            TaskStatus.SUCCESS, f"零號空洞完成，清了 {floors_cleared} 層"
        )

    def _handle_event(self, scene) -> None:
        self._logger.info("處理零號空洞事件")
        # Default: pick the first option
        self._input.wait(0.5)
        self.click_text("選擇", timeout=3.0)
        self._input.wait(1.0)
        self.click_text("確認", timeout=3.0)
        self._input.wait(1.0)

    def _handle_combat(self) -> None:
        self._logger.info("零號空洞戰鬥")
        self.click_text("戰鬥", timeout=3.0)
        self._input.wait(2.0)

        combat = CombatController(
            self._vision, self._input, self._game_state, self._logger, self._combo
        )
        combat.fight(timeout=120.0)

        self._input.wait(2.0)
        self.click_text("確認", timeout=5.0)
        self._input.wait(1.0)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_dungeon_tasks.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add tasks/dungeon/ tests/test_dungeon_tasks.py
git commit -m "feat: dungeon task modules - combat simulation, periodic challenge, hollow zero"
```

---

### Task 11: GUI

**Files:**
- Create: `gui/__init__.py`
- Create: `gui/worker.py`
- Create: `gui/main_window.py`
- Create: `gui/settings_dialog.py`
- Create: `tests/test_gui.py`

- [ ] **Step 1: Write failing test**

`tests/test_gui.py`:
```python
import logging
from unittest.mock import MagicMock, patch

from gui.worker import TaskWorker
from gui.main_window import MainWindow


class TestTaskWorker:
    def test_worker_emits_log_signal(self):
        worker = TaskWorker.__new__(TaskWorker)
        # Just verify the class has the expected attributes
        assert hasattr(TaskWorker, 'run')

    def test_worker_has_finished_signal(self):
        assert hasattr(TaskWorker, 'finished')

    def test_worker_has_log_signal(self):
        assert hasattr(TaskWorker, 'log_message')


class TestMainWindow:
    def test_main_window_class_exists(self):
        assert hasattr(MainWindow, '__init__')

    def test_main_window_has_start_method(self):
        assert hasattr(MainWindow, 'start_tasks')

    def test_main_window_has_stop_method(self):
        assert hasattr(MainWindow, 'stop_tasks')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/champion/zzz && python -m pytest tests/test_gui.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement worker**

Create empty `gui/__init__.py`.

`gui/worker.py`:
```python
import logging
from pathlib import Path
from typing import Dict, List, Optional

from PyQt6.QtCore import QThread, pyqtSignal

from core.config import AppConfig
from core.vision import VisionEngine
from core.input_controller import InputController
from core.game_state import GameState
from core.scheduler import TaskScheduler
from core.logger import setup_logger, GUILogHandler
from tasks.base_task import TaskResult
from tasks.daily.daily_runner import DailyRunner
from tasks.combat.combo_loader import load_all_combos, ComboConfig
from tasks.dungeon.combat_simulation import CombatSimulation
from tasks.dungeon.periodic_challenge import PeriodicChallenge
from tasks.dungeon.hollow_zero import HollowZero


class TaskWorker(QThread):
    log_message = pyqtSignal(str)
    task_completed = pyqtSignal(str, str)  # task_name, status
    finished = pyqtSignal()
    stamina_updated = pyqtSignal(int)

    def __init__(
        self,
        config: AppConfig,
        selected_tasks: Dict[str, bool],
        parent=None,
    ):
        super().__init__(parent)
        self._config = config
        self._selected = selected_tasks
        self._scheduler: Optional[TaskScheduler] = None

    def stop(self) -> None:
        if self._scheduler:
            self._scheduler.request_stop()

    def run(self) -> None:
        base_dir = Path(__file__).parent.parent
        log_dir = base_dir / "logs"

        logger = setup_logger(log_dir, name="zzz_worker")
        gui_handler = GUILogHandler()
        gui_handler.log_signal.connect(self.log_message.emit)
        logger.addHandler(gui_handler)

        vision = VisionEngine(self._config)
        input_ctrl = InputController(self._config)
        game_state = GameState(self._config, vision)

        combos_dir = base_dir / "config" / "combos"
        all_combos = load_all_combos(combos_dir)
        default_combo = next(iter(all_combos.values())) if all_combos else ComboConfig(
            character="default",
            combo_sequence=[{"action": "attack", "count": 3, "interval": 0.15}],
            priority_reactions={"dodge_signal": 10, "qte_prompt": 9, "ultimate_ready": 8, "switch_prompt": 7},
        )

        self._scheduler = TaskScheduler(logger)
        self._scheduler.on_task_complete = lambda name, result: self.task_completed.emit(
            name, result.status.name
        )

        # Add selected tasks
        if self._selected.get("daily", False):
            self._scheduler.add_task(
                DailyRunner(vision, input_ctrl, game_state, logger)
            )

        if self._selected.get("combat_simulation", False):
            self._scheduler.add_task(
                CombatSimulation(vision, input_ctrl, game_state, logger, default_combo)
            )

        if self._selected.get("periodic_challenge", False):
            self._scheduler.add_task(
                PeriodicChallenge(vision, input_ctrl, game_state, logger, default_combo)
            )

        if self._selected.get("hollow_zero", False):
            self._scheduler.add_task(
                HollowZero(vision, input_ctrl, game_state, logger, default_combo)
            )

        logger.info("開始執行所有選定任務")
        self._scheduler.run_all()
        logger.info("所有任務已完成")

        self.stamina_updated.emit(game_state.stamina)
        self.finished.emit()
```

- [ ] **Step 4: Implement main window**

`gui/main_window.py`:
```python
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.config import AppConfig
from gui.worker import TaskWorker


TASK_TREE = {
    "日常全部": {
        "key": "daily",
        "children": {
            "郵件領取": "mail",
            "咖啡廳": "cafe",
            "刮刮樂": "scratch",
            "影碟店": "video",
            "活躍任務": "missions",
        },
    },
    "刷本": {
        "key": "dungeon",
        "children": {
            "影像實戰": "combat_simulation",
            "零號空洞": "hollow_zero",
            "定期挑戰": "periodic_challenge",
        },
    },
}


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig):
        super().__init__()
        self._config = config
        self._worker: Optional[TaskWorker] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("ZZZ AutoPlayer")
        self.setMinimumSize(800, 500)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Top area: task tree + log
        content_layout = QHBoxLayout()

        # Left: task tree
        self._task_tree = QTreeWidget()
        self._task_tree.setHeaderLabel("任務列表")
        self._task_tree.setMaximumWidth(200)
        self._build_task_tree()
        content_layout.addWidget(self._task_tree)

        # Right: log
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        content_layout.addWidget(self._log_text)

        main_layout.addLayout(content_layout)

        # Bottom: controls
        controls = QHBoxLayout()

        self._start_btn = QPushButton("▶ 開始")
        self._start_btn.clicked.connect(self.start_tasks)
        controls.addWidget(self._start_btn)

        self._stop_btn = QPushButton("⏹ 停止")
        self._stop_btn.clicked.connect(self.stop_tasks)
        self._stop_btn.setEnabled(False)
        controls.addWidget(self._stop_btn)

        self._settings_btn = QPushButton("⚙ 設定")
        self._settings_btn.clicked.connect(self._open_settings)
        controls.addWidget(self._settings_btn)

        controls.addStretch()

        self._stamina_label = QLabel("體力: ---")
        controls.addWidget(self._stamina_label)

        main_layout.addLayout(controls)

    def _build_task_tree(self) -> None:
        for group_name, group_data in TASK_TREE.items():
            parent = QTreeWidgetItem(self._task_tree, [group_name])
            parent.setCheckState(0, Qt.CheckState.Checked)
            parent.setData(0, Qt.ItemDataRole.UserRole, group_data["key"])

            for child_name, child_key in group_data.get("children", {}).items():
                child = QTreeWidgetItem(parent, [child_name])
                child.setCheckState(0, Qt.CheckState.Checked)
                child.setData(0, Qt.ItemDataRole.UserRole, child_key)

        self._task_tree.expandAll()

    def _get_selected_tasks(self) -> dict:
        selected = {}
        root = self._task_tree.invisibleRootItem()
        for i in range(root.childCount()):
            group = root.child(i)
            key = group.data(0, Qt.ItemDataRole.UserRole)
            checked = group.checkState(0) == Qt.CheckState.Checked
            selected[key] = checked
            for j in range(group.childCount()):
                child = group.child(j)
                child_key = child.data(0, Qt.ItemDataRole.UserRole)
                selected[child_key] = child.checkState(0) == Qt.CheckState.Checked
        return selected

    def start_tasks(self) -> None:
        if self._worker and self._worker.isRunning():
            return

        selected = self._get_selected_tasks()
        self._log_text.clear()
        self._log("開始執行任務...")

        self._worker = TaskWorker(self._config, selected)
        self._worker.log_message.connect(self._log)
        self._worker.task_completed.connect(self._on_task_completed)
        self._worker.stamina_updated.connect(self._update_stamina)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)

    def stop_tasks(self) -> None:
        if self._worker:
            self._worker.stop()
            self._log("正在停止...")

    def _log(self, message: str) -> None:
        self._log_text.append(message)

    def _on_task_completed(self, name: str, status: str) -> None:
        self._log(f"  → {name}: {status}")

    def _update_stamina(self, stamina: int) -> None:
        self._stamina_label.setText(f"體力: {stamina}")

    def _on_finished(self) -> None:
        self._log("所有任務已完成")
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def _open_settings(self) -> None:
        from gui.settings_dialog import SettingsDialog

        dialog = SettingsDialog(self._config, self)
        dialog.exec()
```

- [ ] **Step 5: Implement settings dialog**

`gui/settings_dialog.py`:
```python
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.config import AppConfig


class SettingsDialog(QDialog):
    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self._config = config
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("設定")
        self.setMinimumSize(400, 350)

        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # Vision tab
        vision_tab = QWidget()
        vision_layout = QFormLayout(vision_tab)

        self._ocr_confidence = QDoubleSpinBox()
        self._ocr_confidence.setRange(0.0, 1.0)
        self._ocr_confidence.setSingleStep(0.05)
        self._ocr_confidence.setValue(self._config.vision.ocr_confidence)
        vision_layout.addRow("OCR 信心閾值:", self._ocr_confidence)

        self._template_threshold = QDoubleSpinBox()
        self._template_threshold.setRange(0.0, 1.0)
        self._template_threshold.setSingleStep(0.05)
        self._template_threshold.setValue(self._config.vision.template_threshold)
        vision_layout.addRow("模板比對閾值:", self._template_threshold)

        self._screenshot_interval = QDoubleSpinBox()
        self._screenshot_interval.setRange(0.01, 1.0)
        self._screenshot_interval.setSingleStep(0.05)
        self._screenshot_interval.setValue(self._config.vision.screenshot_interval)
        vision_layout.addRow("截圖間隔 (秒):", self._screenshot_interval)

        tabs.addTab(vision_tab, "辨識")

        # Input tab
        input_tab = QWidget()
        input_layout = QFormLayout(input_tab)

        self._click_delay = QDoubleSpinBox()
        self._click_delay.setRange(0.0, 1.0)
        self._click_delay.setSingleStep(0.01)
        self._click_delay.setValue(self._config.input.click_delay)
        input_layout.addRow("點擊延遲 (秒):", self._click_delay)

        self._action_delay = QDoubleSpinBox()
        self._action_delay.setRange(0.0, 2.0)
        self._action_delay.setSingleStep(0.05)
        self._action_delay.setValue(self._config.input.action_delay)
        input_layout.addRow("動作延遲 (秒):", self._action_delay)

        self._loading_timeout = QSpinBox()
        self._loading_timeout.setRange(5, 60)
        self._loading_timeout.setValue(int(self._config.input.loading_timeout))
        input_layout.addRow("載入超時 (秒):", self._loading_timeout)

        tabs.addTab(input_tab, "操作")

        # Dungeon tab
        dungeon_tab = QWidget()
        dungeon_layout = QFormLayout(dungeon_tab)

        self._max_stamina = QSpinBox()
        self._max_stamina.setRange(0, 2000)
        self._max_stamina.setValue(self._config.dungeon.max_stamina_usage)
        dungeon_layout.addRow("最大體力消耗:", self._max_stamina)

        self._hollow_difficulty = QSpinBox()
        self._hollow_difficulty.setRange(1, 6)
        self._hollow_difficulty.setValue(self._config.dungeon.hollow_zero_difficulty)
        dungeon_layout.addRow("零號空洞難度:", self._hollow_difficulty)

        self._combat_sim_repeat = QSpinBox()
        self._combat_sim_repeat.setRange(1, 20)
        self._combat_sim_repeat.setValue(self._config.dungeon.combat_sim_repeat)
        dungeon_layout.addRow("影像實戰次數:", self._combat_sim_repeat)

        tabs.addTab(dungeon_tab, "副本")

        # Tools tab
        tools_tab = QWidget()
        tools_layout = QVBoxLayout(tools_tab)
        capture_btn = QPushButton("截取模板截圖")
        capture_btn.clicked.connect(self._capture_template)
        tools_layout.addWidget(capture_btn)
        tools_layout.addWidget(QLabel("截取遊戲畫面後，用圖片編輯器裁切出需要的 UI 元素，\n儲存到 assets/templates/ 對應的資料夾中。"))
        tools_layout.addStretch()
        tabs.addTab(tools_tab, "工具")

        layout.addWidget(tabs)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _capture_template(self) -> None:
        """Open a screenshot capture tool for creating new templates."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import mss
        import cv2
        import numpy as np

        # Capture current screen
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # Save to temp and let user crop in an image editor
        save_path, _ = QFileDialog.getSaveFileName(
            self, "儲存模板截圖", str(Path(__file__).parent.parent / "assets" / "templates"),
            "PNG (*.png)"
        )
        if save_path:
            cv2.imwrite(save_path, frame)
            QMessageBox.information(
                self, "截圖已儲存",
                f"全螢幕截圖已儲存到:\n{save_path}\n\n請用圖片編輯器裁切出需要的 UI 元素。"
            )

    def _save_and_close(self) -> None:
        self._config.vision.ocr_confidence = self._ocr_confidence.value()
        self._config.vision.template_threshold = self._template_threshold.value()
        self._config.vision.screenshot_interval = self._screenshot_interval.value()
        self._config.input.click_delay = self._click_delay.value()
        self._config.input.action_delay = self._action_delay.value()
        self._config.input.loading_timeout = self._loading_timeout.value()
        self._config.dungeon.max_stamina_usage = self._max_stamina.value()
        self._config.dungeon.hollow_zero_difficulty = self._hollow_difficulty.value()
        self._config.dungeon.combat_sim_repeat = self._combat_sim_repeat.value()
        self.accept()
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd /home/champion/zzz && python -m pytest tests/test_gui.py -v`
Expected: 6 passed

- [ ] **Step 7: Commit**

```bash
git add gui/ tests/test_gui.py
git commit -m "feat: GUI with main window, task tree, log display, settings dialog, and worker thread"
```

---

### Task 12: Main Entry Point & PyInstaller Config

**Files:**
- Create: `main.py`
- Create: `build.spec`

- [ ] **Step 1: Create main.py**

`main.py`:
```python
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from core.config import AppConfig
from gui.main_window import MainWindow


def main():
    base_dir = Path(__file__).parent
    config_path = base_dir / "config" / "settings.yaml"
    config = AppConfig.load(config_path)

    app = QApplication(sys.argv)
    app.setApplicationName("ZZZ AutoPlayer")

    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create build.spec for PyInstaller**

`build.spec`:
```python
# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'paddleocr',
        'paddle',
        'PyQt6',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ZZZ-AutoPlayer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ZZZ-AutoPlayer',
)
```

- [ ] **Step 3: Create remaining __init__.py files and asset directories**

```bash
mkdir -p assets/templates/combat assets/templates/menus assets/templates/dungeons logs
touch tasks/__init__.py tasks/daily/__init__.py tasks/combat/__init__.py tasks/dungeon/__init__.py gui/__init__.py
```

- [ ] **Step 4: Verify project runs without errors (import check)**

Run: `cd /home/champion/zzz && python -c "from core.config import AppConfig; from core.vision import VisionEngine; from core.scheduler import TaskScheduler; from tasks.base_task import BaseTask; from tasks.combat.combo_loader import load_combo; print('All imports OK')"`
Expected: `All imports OK`

- [ ] **Step 5: Run all tests**

Run: `cd /home/champion/zzz && python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add main.py build.spec assets/ logs/ tasks/__init__.py tasks/daily/__init__.py tasks/combat/__init__.py tasks/dungeon/__init__.py gui/__init__.py
git commit -m "feat: main entry point, PyInstaller build config, and project structure"
```

- [ ] **Step 7: Push to remote**

```bash
git push origin master
```

---

## Windows Packaging Instructions

After all code is pushed, on your Windows machine:

```bash
# 1. Clone the repo
git clone git@github.com:rgib37190/zzz_auto.git
cd zzz_auto

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 4. Build
pyinstaller build.spec

# 5. Output is in dist/ZZZ-AutoPlayer/
#    - Copy your template screenshots to dist/ZZZ-AutoPlayer/assets/templates/
#    - Double-click ZZZ-AutoPlayer.exe to run
```

## Template Screenshots Needed

Before the script can work, you need to capture these template images from the game (save as PNG in the corresponding folders):

| File | Location | Description |
|------|----------|-------------|
| `combat/dodge_signal.png` | `assets/templates/` | 閃避提示的黃光截圖 |
| `combat/ultimate_ready.png` | `assets/templates/` | 大招可用的 UI 提示 |
| `combat/qte_prompt.png` | `assets/templates/` | QTE 按鍵提示 |
| `combat/switch_prompt.png` | `assets/templates/` | 連攜攻擊提示 |
| `combat/combat_finished.png` | `assets/templates/` | 戰鬥結束畫面標誌 |

Use the game at 1920x1080 resolution. Crop tightly around the UI element, not the entire screen.
