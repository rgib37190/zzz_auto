import logging
from unittest.mock import MagicMock

from tasks.base_task import BaseTask, TaskResult, TaskStatus


class ConcreteTask(BaseTask):
    def __init__(self, *args, should_fail=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._should_fail = should_fail
        self.executed = False

    @property
    def name(self) -> str:
        return "test_task"

    def execute(self) -> TaskResult:
        self.executed = True
        if self._should_fail:
            return TaskResult(TaskStatus.FAILED, "something broke")
        return TaskResult(TaskStatus.SUCCESS, "done")


class TestBaseTask:
    def setup_method(self):
        self.vision = MagicMock()
        self.input = MagicMock()
        self.game_state = MagicMock()
        self.logger = logging.getLogger("test")

    def test_run_success(self):
        task = ConcreteTask(self.vision, self.input, self.game_state, self.logger)
        result = task.run()
        assert result.status == TaskStatus.SUCCESS
        assert task.executed is True

    def test_run_failure(self):
        task = ConcreteTask(
            self.vision, self.input, self.game_state, self.logger, should_fail=True
        )
        result = task.run()
        assert result.status == TaskStatus.FAILED

    def test_run_catches_exception(self):
        task = ConcreteTask(self.vision, self.input, self.game_state, self.logger)
        task.execute = MagicMock(side_effect=RuntimeError("crash"))
        result = task.run()
        assert result.status == TaskStatus.ERROR
        assert "crash" in result.message

    def test_stop_flag(self):
        task = ConcreteTask(self.vision, self.input, self.game_state, self.logger)
        assert task.should_stop is False
        task.request_stop()
        assert task.should_stop is True
