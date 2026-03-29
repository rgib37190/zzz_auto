from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

from core.config import AppConfig
from gui.worker import TaskWorker


TASK_TREE = {
    "日常全部": {
        "key": "daily",
        "children": {
            "郵件領取": "mail",
            "咖啡廳": "cafe",
            "刮刮樂": "scratch",
            "影碟店": "video",
            "活躍任務": "missions",
        },
    },
    "刷本": {
        "key": "dungeon",
        "children": {
            "影像實戰": "combat_simulation",
            "零號空洞": "hollow_zero",
            "定期挑戰": "periodic_challenge",
        },
    },
}


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig):
        super().__init__()
        self._config = config
        self._worker: Optional[TaskWorker] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("ZZZ AutoPlayer")
        self.setMinimumSize(800, 500)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        content_layout = QHBoxLayout()

        self._task_tree = QTreeWidget()
        self._task_tree.setHeaderLabel("任務列表")
        self._task_tree.setMaximumWidth(200)
        self._build_task_tree()
        content_layout.addWidget(self._task_tree)

        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        content_layout.addWidget(self._log_text)

        main_layout.addLayout(content_layout)

        controls = QHBoxLayout()

        self._start_btn = QPushButton("▶ 開始")
        self._start_btn.clicked.connect(self.start_tasks)
        controls.addWidget(self._start_btn)

        self._stop_btn = QPushButton("⏹ 停止")
        self._stop_btn.clicked.connect(self.stop_tasks)
        self._stop_btn.setEnabled(False)
        controls.addWidget(self._stop_btn)

        self._settings_btn = QPushButton("⚙ 設定")
        self._settings_btn.clicked.connect(self._open_settings)
        controls.addWidget(self._settings_btn)

        controls.addStretch()

        self._stamina_label = QLabel("體力: ---")
        controls.addWidget(self._stamina_label)

        main_layout.addLayout(controls)

    def _build_task_tree(self) -> None:
        for group_name, group_data in TASK_TREE.items():
            parent = QTreeWidgetItem(self._task_tree, [group_name])
            parent.setCheckState(0, Qt.CheckState.Checked)
            parent.setData(0, Qt.ItemDataRole.UserRole, group_data["key"])
            for child_name, child_key in group_data.get("children", {}).items():
                child = QTreeWidgetItem(parent, [child_name])
                child.setCheckState(0, Qt.CheckState.Checked)
                child.setData(0, Qt.ItemDataRole.UserRole, child_key)
        self._task_tree.expandAll()

    def _get_selected_tasks(self) -> dict:
        selected = {}
        root = self._task_tree.invisibleRootItem()
        for i in range(root.childCount()):
            group = root.child(i)
            key = group.data(0, Qt.ItemDataRole.UserRole)
            checked = group.checkState(0) == Qt.CheckState.Checked
            selected[key] = checked
            for j in range(group.childCount()):
                child = group.child(j)
                child_key = child.data(0, Qt.ItemDataRole.UserRole)
                selected[child_key] = child.checkState(0) == Qt.CheckState.Checked
        return selected

    def start_tasks(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        selected = self._get_selected_tasks()
        self._log_text.clear()
        self._log("開始執行任務...")
        self._worker = TaskWorker(self._config, selected)
        self._worker.log_message.connect(self._log)
        self._worker.task_completed.connect(self._on_task_completed)
        self._worker.stamina_updated.connect(self._update_stamina)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)

    def stop_tasks(self) -> None:
        if self._worker:
            self._worker.stop()
            self._log("正在停止...")

    def _log(self, message: str) -> None:
        self._log_text.append(message)

    def _on_task_completed(self, name: str, status: str) -> None:
        self._log(f"  → {name}: {status}")

    def _update_stamina(self, stamina: int) -> None:
        self._stamina_label.setText(f"體力: {stamina}")

    def _on_finished(self) -> None:
        self._log("所有任務已完成")
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def _open_settings(self) -> None:
        from gui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self._config, self)
        dialog.exec()
