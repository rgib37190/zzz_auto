import logging
from unittest.mock import MagicMock

from tasks.base_task import TaskResult, TaskStatus
from tasks.daily.daily_runner import DailyRunner
from tasks.daily.mail_collector import MailCollector
from tasks.daily.cafe_manager import CafeManager
from tasks.daily.scratch_card import ScratchCard
from tasks.daily.video_store import VideoStore
from tasks.daily.active_missions import ActiveMissions


class TestDailyRunner:
    def setup_method(self):
        self.vision = MagicMock()
        self.input_ctrl = MagicMock()
        self.game_state = MagicMock()
        self.logger = logging.getLogger("test_daily")

    def test_daily_runner_name(self):
        runner = DailyRunner(self.vision, self.input_ctrl, self.game_state, self.logger)
        assert runner.name == "daily_runner"

    def test_daily_runner_has_all_subtasks(self):
        runner = DailyRunner(self.vision, self.input_ctrl, self.game_state, self.logger)
        names = [t.name for t in runner.subtasks]
        assert "mail_collector" in names
        assert "cafe_manager" in names
        assert "scratch_card" in names
        assert "video_store" in names
        assert "active_missions" in names

    def test_daily_runner_continues_on_subtask_failure(self):
        runner = DailyRunner(self.vision, self.input_ctrl, self.game_state, self.logger)
        runner.subtasks[0].execute = MagicMock(
            return_value=TaskResult(TaskStatus.FAILED, "fail")
        )
        for task in runner.subtasks[1:]:
            task.execute = MagicMock(
                return_value=TaskResult(TaskStatus.SUCCESS, "ok")
            )
        result = runner.execute()
        assert result.status == TaskStatus.SUCCESS
        for task in runner.subtasks[1:]:
            task.execute.assert_called_once()


class TestMailCollector:
    def test_name(self):
        task = MailCollector(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        assert task.name == "mail_collector"

class TestCafeManager:
    def test_name(self):
        task = CafeManager(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        assert task.name == "cafe_manager"

class TestScratchCard:
    def test_name(self):
        task = ScratchCard(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        assert task.name == "scratch_card"

class TestVideoStore:
    def test_name(self):
        task = VideoStore(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        assert task.name == "video_store"

class TestActiveMissions:
    def test_name(self):
        task = ActiveMissions(MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"))
        assert task.name == "active_missions"
