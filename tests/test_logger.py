import logging
from pathlib import Path

from core.logger import setup_logger, GUILogHandler


class TestSetupLogger:
    def test_creates_file_handler(self, tmp_path):
        logger = setup_logger(log_dir=tmp_path, name="test_creates_file_handler")
        logger.info("test message")
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) == 1
        content = log_files[0].read_text()
        assert "test message" in content

    def test_log_file_named_by_date(self, tmp_path):
        from datetime import date

        logger = setup_logger(log_dir=tmp_path, name="test_log_file_named_by_date")
        logger.info("hello")
        expected_name = f"{date.today().isoformat()}.log"
        assert (tmp_path / expected_name).exists()


class TestGUILogHandler:
    def test_emits_signal_on_log(self, tmp_path):
        received = []
        handler = GUILogHandler()
        handler.log_signal.connect(lambda msg: received.append(msg))
        logger = setup_logger(log_dir=tmp_path, name="test_emits_signal_on_log")
        logger.addHandler(handler)
        logger.info("gui test")
        assert any("gui test" in msg for msg in received)
