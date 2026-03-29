from unittest.mock import MagicMock
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
