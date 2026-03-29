import logging
from unittest.mock import MagicMock

from core.scheduler import TaskScheduler
from tasks.base_task import BaseTask, TaskResult, TaskStatus


class FakeTask(BaseTask):
    def __init__(self, name_str, result_status=TaskStatus.SUCCESS, **kwargs):
        super().__init__(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        self._name = name_str
        self._result_status = result_status

    @property
    def name(self):
        return self._name

    def execute(self):
        return TaskResult(self._result_status, f"{self._name} done")


class TestTaskScheduler:
    def test_run_empty_queue(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        results = scheduler.run_all()
        assert results == []

    def test_run_single_task(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        scheduler.add_task(FakeTask("task1"))
        results = scheduler.run_all()
        assert len(results) == 1
        assert results[0].status == TaskStatus.SUCCESS

    def test_run_multiple_tasks_in_order(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        order = []
        t1 = FakeTask("first")
        t2 = FakeTask("second")
        original_run1 = t1.run
        original_run2 = t2.run

        def tracked_run1():
            order.append("first")
            return original_run1()

        def tracked_run2():
            order.append("second")
            return original_run2()

        t1.run = tracked_run1
        t2.run = tracked_run2
        scheduler.add_task(t1)
        scheduler.add_task(t2)
        scheduler.run_all()
        assert order == ["first", "second"]

    def test_failed_task_does_not_stop_others(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        scheduler.add_task(FakeTask("fail", TaskStatus.FAILED))
        scheduler.add_task(FakeTask("ok", TaskStatus.SUCCESS))
        results = scheduler.run_all()
        assert len(results) == 2
        assert results[0].status == TaskStatus.FAILED
        assert results[1].status == TaskStatus.SUCCESS

    def test_stop_cancels_remaining(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        scheduler.add_task(FakeTask("t1"))
        scheduler.add_task(FakeTask("t2"))
        scheduler.request_stop()
        results = scheduler.run_all()
        assert len(results) == 0

    def test_on_task_complete_callback(self):
        scheduler = TaskScheduler(logging.getLogger("t"))
        completed = []
        scheduler.on_task_complete = lambda name, result: completed.append(name)
        scheduler.add_task(FakeTask("a"))
        scheduler.add_task(FakeTask("b"))
        scheduler.run_all()
        assert completed == ["a", "b"]
