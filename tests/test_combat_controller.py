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
        # Load a fake template so detection has something to check
        self.ctrl._templates["dodge_signal"] = np.zeros((10, 10, 3), dtype=np.uint8)
        self.vision.find_template.return_value = (960, 540, 0.9)
        signals = self.ctrl.detect_signals(self.scene)
        assert "dodge_signal" in signals

    def test_detect_no_signals(self):
        self.ctrl._templates["dodge_signal"] = np.zeros((10, 10, 3), dtype=np.uint8)
        self.vision.find_template.return_value = None
        signals = self.ctrl.detect_signals(self.scene)
        assert len(signals) == 0

    def test_highest_priority_signal_wins(self):
        signals = {"dodge_signal", "ultimate_ready"}
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
        self.input_ctrl.press_key.assert_called()
