import logging
from typing import Callable, List, Optional

from tasks.base_task import BaseTask, TaskResult, TaskStatus


class TaskScheduler:
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._tasks: List[BaseTask] = []
        self._stop_requested = False
        self.on_task_complete: Optional[Callable[[str, TaskResult], None]] = None

    def add_task(self, task: BaseTask) -> None:
        self._tasks.append(task)

    def clear(self) -> None:
        self._tasks.clear()

    def request_stop(self) -> None:
        self._stop_requested = True
        for task in self._tasks:
            task.request_stop()

    def run_all(self) -> List[TaskResult]:
        results = []
        for task in self._tasks:
            if self._stop_requested:
                self._logger.info("排程已停止，跳過剩餘任務")
                break
            result = task.run()
            results.append(result)
            if self.on_task_complete:
                self.on_task_complete(task.name, result)
            if result.status == TaskStatus.ERROR:
                self._logger.error(f"任務 {task.name} 發生錯誤: {result.message}")
        self._tasks.clear()
        return results
