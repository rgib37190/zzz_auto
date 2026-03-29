import logging
from tasks.base_task import BaseTask, TaskResult, TaskStatus

class MailCollector(BaseTask):
    @property
    def name(self) -> str:
        return "mail_collector"

    def execute(self) -> TaskResult:
        self._logger.info("開始領取郵件")
        if not self.click_text("郵件"):
            if not self.click_text("信箱"):
                return TaskResult(TaskStatus.FAILED, "找不到郵件入口")
        self._input.wait(1.0)
        if self.click_text("全部領取", timeout=3.0):
            self._logger.info("已領取所有郵件")
            self._input.wait(1.0)
            self.click_text("確認", timeout=3.0)
        else:
            self._logger.info("沒有新郵件")
        self._input.press_key("escape")
        self._input.wait(0.5)
        return TaskResult(TaskStatus.SUCCESS, "郵件領取完成")
