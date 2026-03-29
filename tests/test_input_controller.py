import time
from unittest.mock import patch, MagicMock, call

from core.input_controller import InputController
from core.config import AppConfig


class TestInputController:
    def setup_method(self):
        self.config = AppConfig()
        self.controller = InputController(self.config)

    @patch("core.input_controller.pyautogui")
    def test_click(self, mock_pag):
        self.controller.click(100, 200)
        mock_pag.click.assert_called_once_with(100, 200)

    @patch("core.input_controller.pyautogui")
    def test_click_with_delay(self, mock_pag):
        self.controller.click(100, 200)
        # Should not throw
        assert mock_pag.click.called

    @patch("core.input_controller.pyautogui")
    def test_press_key(self, mock_pag):
        self.controller.press_key("space")
        mock_pag.press.assert_called_once_with("space")

    @patch("core.input_controller.pyautogui")
    def test_hold_key(self, mock_pag):
        self.controller.hold_key("e", duration=0.5)
        mock_pag.keyDown.assert_called_once_with("e")
        mock_pag.keyUp.assert_called_once_with("e")

    @patch("core.input_controller.pyautogui")
    def test_press_key_multiple(self, mock_pag):
        self.controller.press_key_multiple("j", count=3, interval=0.1)
        assert mock_pag.press.call_count == 3

    @patch("core.input_controller.pyautogui")
    def test_move_mouse(self, mock_pag):
        self.controller.move_to(500, 300)
        mock_pag.moveTo.assert_called_once_with(500, 300)

    @patch("core.input_controller.pyautogui")
    def test_drag(self, mock_pag):
        self.controller.drag(100, 100, 200, 200, duration=0.3)
        mock_pag.moveTo.assert_called_once_with(100, 100)
        mock_pag.drag.assert_called_once_with(200, 200, duration=0.3)
