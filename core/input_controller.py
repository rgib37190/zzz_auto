import time

import pyautogui

from core.config import AppConfig

# Disable PyAutoGUI's built-in pause and failsafe for automation
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False


class InputController:
    def __init__(self, config: AppConfig):
        self._config = config

    def click(self, x: int, y: int) -> None:
        pyautogui.click(x, y)
        time.sleep(self._config.input.click_delay)

    def double_click(self, x: int, y: int) -> None:
        pyautogui.doubleClick(x, y)
        time.sleep(self._config.input.click_delay)

    def press_key(self, key: str) -> None:
        pyautogui.press(key)
        time.sleep(self._config.input.click_delay)

    def hold_key(self, key: str, duration: float = 0.5) -> None:
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)
        time.sleep(self._config.input.click_delay)

    def press_key_multiple(self, key: str, count: int, interval: float = 0.15) -> None:
        for _ in range(count):
            pyautogui.press(key)
            time.sleep(interval)

    def move_to(self, x: int, y: int) -> None:
        pyautogui.moveTo(x, y)

    def drag(self, start_x: int, start_y: int, dx: int, dy: int, duration: float = 0.5) -> None:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.drag(dx, dy, duration=duration)

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)
