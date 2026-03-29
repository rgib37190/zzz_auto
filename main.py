import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from core.config import AppConfig
from gui.main_window import MainWindow


def main():
    base_dir = Path(__file__).parent
    config_path = base_dir / "config" / "settings.yaml"
    config = AppConfig.load(config_path)

    app = QApplication(sys.argv)
    app.setApplicationName("ZZZ AutoPlayer")

    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
