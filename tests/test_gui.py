import logging
from unittest.mock import MagicMock, patch

from gui.worker import TaskWorker
from gui.main_window import MainWindow


class TestTaskWorker:
    def test_worker_has_run_method(self):
        assert hasattr(TaskWorker, 'run')

    def test_worker_has_finished_signal(self):
        assert hasattr(TaskWorker, 'finished')

    def test_worker_has_log_signal(self):
        assert hasattr(TaskWorker, 'log_message')


class TestMainWindow:
    def test_main_window_class_exists(self):
        assert hasattr(MainWindow, '__init__')

    def test_main_window_has_start_method(self):
        assert hasattr(MainWindow, 'start_tasks')

    def test_main_window_has_stop_method(self):
        assert hasattr(MainWindow, 'stop_tasks')
