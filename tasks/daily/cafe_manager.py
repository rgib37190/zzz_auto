import logging
from tasks.base_task import BaseTask, TaskResult, TaskStatus

class CafeManager(BaseTask):
    @property
    def name(self) -> str:
        return "cafe_manager"

    def execute(self) -> TaskResult:
        self._logger.info("開始處理咖啡廳")
        if not self.click_text("咖啡廳"):
            return TaskResult(TaskStatus.FAILED, "找不到咖啡廳入口")
        self._input.wait(2.0)
        if self.click_text("營收", timeout=5.0):
            self._logger.info("已收取咖啡廳營收")
            self._input.wait(1.0)
            self.click_text("確認", timeout=3.0)
        self._input.wait(1.0)
        self._input.press_key("escape")
        self._input.wait(0.5)
        return TaskResult(TaskStatus.SUCCESS, "咖啡廳處理完成")
