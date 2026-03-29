import logging
from typing import List
from tasks.base_task import BaseTask, TaskResult, TaskStatus
from tasks.daily.mail_collector import MailCollector
from tasks.daily.cafe_manager import CafeManager
from tasks.daily.scratch_card import ScratchCard
from tasks.daily.video_store import VideoStore
from tasks.daily.active_missions import ActiveMissions

class DailyRunner(BaseTask):
    def __init__(self, vision, input_ctrl, game_state, logger: logging.Logger):
        super().__init__(vision, input_ctrl, game_state, logger)
        self.subtasks: List[BaseTask] = [
            MailCollector(vision, input_ctrl, game_state, logger),
            CafeManager(vision, input_ctrl, game_state, logger),
            ScratchCard(vision, input_ctrl, game_state, logger),
            VideoStore(vision, input_ctrl, game_state, logger),
            ActiveMissions(vision, input_ctrl, game_state, logger),
        ]

    @property
    def name(self) -> str:
        return "daily_runner"

    def request_stop(self) -> None:
        super().request_stop()
        for task in self.subtasks:
            task.request_stop()

    def execute(self) -> TaskResult:
        self._logger.info("開始執行日常任務")
        results = []
        for task in self.subtasks:
            if self.should_stop:
                break
            result = task.run()
            results.append((task.name, result))
        succeeded = sum(1 for _, r in results if r.status == TaskStatus.SUCCESS)
        total = len(results)
        self._logger.info(f"日常任務完成: {succeeded}/{total} 成功")
        return TaskResult(TaskStatus.SUCCESS, f"日常任務: {succeeded}/{total} 成功")
