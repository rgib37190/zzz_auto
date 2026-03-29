from pathlib import Path
from typing import Dict, Optional

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
    task_completed = pyqtSignal(str, str)
    finished = pyqtSignal()
    stamina_updated = pyqtSignal(int)

    def __init__(self, config: AppConfig, selected_tasks: Dict[str, bool], parent=None):
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

        if self._selected.get("daily", False):
            self._scheduler.add_task(DailyRunner(vision, input_ctrl, game_state, logger))

        if self._selected.get("combat_simulation", False):
            self._scheduler.add_task(CombatSimulation(vision, input_ctrl, game_state, logger, default_combo))

        if self._selected.get("periodic_challenge", False):
            self._scheduler.add_task(PeriodicChallenge(vision, input_ctrl, game_state, logger, default_combo))

        if self._selected.get("hollow_zero", False):
            self._scheduler.add_task(HollowZero(vision, input_ctrl, game_state, logger, default_combo))

        logger.info("開始執行所有選定任務")
        self._scheduler.run_all()
        logger.info("所有任務已完成")

        self.stamina_updated.emit(game_state.stamina)
        self.finished.emit()
