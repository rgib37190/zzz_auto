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
