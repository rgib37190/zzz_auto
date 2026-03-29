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
        for screen, markers in SCREEN_TEXT_MARKERS.items():
            for marker in markers:
                result = self._vision.find_text(scene, marker)
                if result is not None:
                    return screen

        return Screen.UNKNOWN

    def is_loading(self, scene: np.ndarray) -> bool:
        gray = scene.mean()
        return bool(gray < 15)  # Nearly black = loading screen
