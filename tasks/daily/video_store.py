import logging
from tasks.base_task import BaseTask, TaskResult, TaskStatus

class VideoStore(BaseTask):
    @property
    def name(self) -> str:
        return "video_store"

    def execute(self) -> TaskResult:
        self._logger.info("開始處理影碟店")
        if not self.click_text("影碟店"):
            return TaskResult(TaskStatus.SKIPPED, "找不到影碟店入口")
        self._input.wait(1.5)
        self.click_text("租借", timeout=3.0)
        self._input.wait(1.0)
        self.click_text("確認", timeout=3.0)
        self._input.press_key("escape")
        self._input.wait(0.5)
        return TaskResult(TaskStatus.SUCCESS, "影碟店處理完成")
