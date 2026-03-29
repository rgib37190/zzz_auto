import logging
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
        if not self.click_text("影像實戰"):
            if not self.click_text("實戰模擬"):
                return TaskResult(TaskStatus.FAILED, "找不到影像實戰入口")
        self._input.wait(1.5)
        run_count = 0
        while not self.should_stop and self._game_state.can_spend_stamina(STAMINA_PER_RUN):
            if not self.click_text("挑戰", timeout=5.0):
                break
            self._input.wait(2.0)
            combat = CombatController(
                self._vision, self._input, self._game_state, self._logger, self._combo
            )
            combat.fight(timeout=120.0)
            self._input.wait(2.0)
            self.click_text("確認", timeout=5.0)
            self._input.wait(1.0)
            self._game_state.consume_stamina(STAMINA_PER_RUN)
            run_count += 1
            self._logger.info(f"影像實戰第 {run_count} 輪完成")
            if not self.click_text("再次挑戰", timeout=3.0):
                break
        self._input.press_key("escape")
        self._input.wait(0.5)
        return TaskResult(TaskStatus.SUCCESS, f"影像實戰完成 {run_count} 輪")
