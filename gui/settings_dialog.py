from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout,
    QLabel, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget,
)

from core.config import AppConfig


class SettingsDialog(QDialog):
    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self._config = config
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("設定")
        self.setMinimumSize(400, 350)

        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # Vision tab
        vision_tab = QWidget()
        vision_layout = QFormLayout(vision_tab)

        self._ocr_confidence = QDoubleSpinBox()
        self._ocr_confidence.setRange(0.0, 1.0)
        self._ocr_confidence.setSingleStep(0.05)
        self._ocr_confidence.setValue(self._config.vision.ocr_confidence)
        vision_layout.addRow("OCR 信心閾值:", self._ocr_confidence)

        self._template_threshold = QDoubleSpinBox()
        self._template_threshold.setRange(0.0, 1.0)
        self._template_threshold.setSingleStep(0.05)
        self._template_threshold.setValue(self._config.vision.template_threshold)
        vision_layout.addRow("模板比對閾值:", self._template_threshold)

        self._screenshot_interval = QDoubleSpinBox()
        self._screenshot_interval.setRange(0.01, 1.0)
        self._screenshot_interval.setSingleStep(0.05)
        self._screenshot_interval.setValue(self._config.vision.screenshot_interval)
        vision_layout.addRow("截圖間隔 (秒):", self._screenshot_interval)

        tabs.addTab(vision_tab, "辨識")

        # Input tab
        input_tab = QWidget()
        input_layout = QFormLayout(input_tab)

        self._click_delay = QDoubleSpinBox()
        self._click_delay.setRange(0.0, 1.0)
        self._click_delay.setSingleStep(0.01)
        self._click_delay.setValue(self._config.input.click_delay)
        input_layout.addRow("點擊延遲 (秒):", self._click_delay)

        self._action_delay = QDoubleSpinBox()
        self._action_delay.setRange(0.0, 2.0)
        self._action_delay.setSingleStep(0.05)
        self._action_delay.setValue(self._config.input.action_delay)
        input_layout.addRow("動作延遲 (秒):", self._action_delay)

        self._loading_timeout = QSpinBox()
        self._loading_timeout.setRange(5, 60)
        self._loading_timeout.setValue(int(self._config.input.loading_timeout))
        input_layout.addRow("載入超時 (秒):", self._loading_timeout)

        tabs.addTab(input_tab, "操作")

        # Dungeon tab
        dungeon_tab = QWidget()
        dungeon_layout = QFormLayout(dungeon_tab)

        self._max_stamina = QSpinBox()
        self._max_stamina.setRange(0, 2000)
        self._max_stamina.setValue(self._config.dungeon.max_stamina_usage)
        dungeon_layout.addRow("最大體力消耗:", self._max_stamina)

        self._hollow_difficulty = QSpinBox()
        self._hollow_difficulty.setRange(1, 6)
        self._hollow_difficulty.setValue(self._config.dungeon.hollow_zero_difficulty)
        dungeon_layout.addRow("零號空洞難度:", self._hollow_difficulty)

        self._combat_sim_repeat = QSpinBox()
        self._combat_sim_repeat.setRange(1, 20)
        self._combat_sim_repeat.setValue(self._config.dungeon.combat_sim_repeat)
        dungeon_layout.addRow("影像實戰次數:", self._combat_sim_repeat)

        tabs.addTab(dungeon_tab, "副本")

        # Tools tab
        tools_tab = QWidget()
        tools_layout = QVBoxLayout(tools_tab)
        capture_btn = QPushButton("截取模板截圖")
        capture_btn.clicked.connect(self._capture_template)
        tools_layout.addWidget(capture_btn)
        tools_layout.addWidget(QLabel("截取遊戲畫面後，用圖片編輯器裁切出需要的 UI 元素，\n儲存到 assets/templates/ 對應的資料夾中。"))
        tools_layout.addStretch()
        tabs.addTab(tools_tab, "工具")

        layout.addWidget(tabs)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _capture_template(self) -> None:
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import mss
        import cv2
        import numpy as np

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        save_path, _ = QFileDialog.getSaveFileName(
            self, "儲存模板截圖", str(Path(__file__).parent.parent / "assets" / "templates"),
            "PNG (*.png)"
        )
        if save_path:
            cv2.imwrite(save_path, frame)
            QMessageBox.information(
                self, "截圖已儲存",
                f"全螢幕截圖已儲存到:\n{save_path}\n\n請用圖片編輯器裁切出需要的 UI 元素。"
            )

    def _save_and_close(self) -> None:
        self._config.vision.ocr_confidence = self._ocr_confidence.value()
        self._config.vision.template_threshold = self._template_threshold.value()
        self._config.vision.screenshot_interval = self._screenshot_interval.value()
        self._config.input.click_delay = self._click_delay.value()
        self._config.input.action_delay = self._action_delay.value()
        self._config.input.loading_timeout = self._loading_timeout.value()
        self._config.dungeon.max_stamina_usage = self._max_stamina.value()
        self._config.dungeon.hollow_zero_difficulty = self._hollow_difficulty.value()
        self._config.dungeon.combat_sim_repeat = self._combat_sim_repeat.value()
        self.accept()
