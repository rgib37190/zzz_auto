import logging
from tasks.base_task import BaseTask, TaskResult, TaskStatus

class ScratchCard(BaseTask):
    @property
    def name(self) -> str:
        return "scratch_card"

    def execute(self) -> TaskResult:
        self._logger.info("開始刮刮樂")
        if not self.click_text("刮刮樂"):
            return TaskResult(TaskStatus.SKIPPED, "找不到刮刮樂入口")
        self._input.wait(1.0)
        self._input.drag(760, 440, 400, 0, duration=0.5)
        self._input.wait(0.3)
        self._input.drag(760, 540, 400, 0, duration=0.5)
        self._input.wait(0.3)
        self._input.drag(760, 640, 400, 0, duration=0.5)
        self._input.wait(1.0)
        self.click_text("確認", timeout=3.0)
        self._input.press_key("escape")
        self._input.wait(0.5)
        return TaskResult(TaskStatus.SUCCESS, "刮刮樂完成")
