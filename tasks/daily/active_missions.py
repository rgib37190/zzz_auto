import logging
from tasks.base_task import BaseTask, TaskResult, TaskStatus

class ActiveMissions(BaseTask):
    @property
    def name(self) -> str:
        return "active_missions"

    def execute(self) -> TaskResult:
        self._logger.info("開始每日活躍任務")
        if not self.click_text("每日"):
            if not self.click_text("活躍"):
                return TaskResult(TaskStatus.FAILED, "找不到每日任務入口")
        self._input.wait(1.5)
        claimed = 0
        for _ in range(5):
            if self.click_text("領取", timeout=2.0):
                claimed += 1
                self._input.wait(0.5)
                self.click_text("確認", timeout=2.0)
                self._input.wait(0.5)
            else:
                break
        self._logger.info(f"領取了 {claimed} 個活躍獎勵")
        self._input.press_key("escape")
        self._input.wait(0.5)
        return TaskResult(TaskStatus.SUCCESS, f"活躍任務完成，領取 {claimed} 個獎勵")
