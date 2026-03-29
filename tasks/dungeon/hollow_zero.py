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
        if not self.click_text("零號空洞"):
            return TaskResult(TaskStatus.FAILED, "找不到零號空洞入口")
        self._input.wait(2.0)
        if not self.click_text("進入", timeout=5.0):
            return TaskResult(TaskStatus.FAILED, "找不到進入按鈕")
        self._input.wait(2.0)
        floors_cleared = 0
        max_floors = 20
        while not self.should_stop and floors_cleared < max_floors:
            scene = self._vision.capture_screen()
            result = self._vision.find_text(scene, "結算")
            if result:
                self._logger.info("零號空洞探索結束")
                self.click_text("確認", timeout=5.0)
                break
            event_result = self._vision.find_text(scene, "選擇")
            if event_result:
                self._handle_event(scene)
                continue
            combat_result = self._vision.find_text(scene, "戰鬥")
            if combat_result:
                self._handle_combat()
                floors_cleared += 1
                continue
            if not self.click_text("前進", timeout=3.0):
                self._input.click(960, 540)
                self._input.wait(1.0)
            self._input.wait(0.5)
        self._input.press_key("escape")
        self._input.wait(0.5)
        return TaskResult(TaskStatus.SUCCESS, f"零號空洞完成，清了 {floors_cleared} 層")

    def _handle_event(self, scene) -> None:
        self._logger.info("處理零號空洞事件")
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
