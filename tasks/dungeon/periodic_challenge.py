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
        if not self.click_text("定期挑戰"):
            return TaskResult(TaskStatus.FAILED, "找不到定期挑戰入口")
        self._input.wait(1.5)
        if not self.click_text("挑戰", timeout=5.0):
            return TaskResult(TaskStatus.FAILED, "找不到挑戰按鈕")
        self._input.wait(2.0)
        combat = CombatController(
            self._vision, self._input, self._game_state, self._logger, self._combo
        )
        success = combat.fight(timeout=180.0)
        self._input.wait(2.0)
        self.click_text("確認", timeout=5.0)
        self._input.wait(1.0)
        self._input.press_key("escape")
        self._input.wait(0.5)
        if success:
            return TaskResult(TaskStatus.SUCCESS, "定期挑戰完成")
        return TaskResult(TaskStatus.FAILED, "定期挑戰戰鬥失敗")
