import logging
import time
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set

import numpy as np

from tasks.combat.combo_loader import ComboConfig

# Key mappings for ZZZ combat
KEY_MAP = {
    "attack": "j",
    "skill": "e",
    "dodge": "space",
    "ultimate": "q",
    "dash": "shift",
    "switch_1": "space",
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
    def __init__(self, vision, input_ctrl, game_state, logger: logging.Logger, combo: ComboConfig):
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
