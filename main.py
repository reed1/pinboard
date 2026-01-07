from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from window import MainWindow, load_user_config


def main() -> None:
    if len(sys.argv) < 2:
        print("Error: YAML file path is required", file=sys.stderr)
        print("Usage: pinboard <path/to/notes.yaml>", file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])

    app = QApplication(sys.argv)
    window = MainWindow(file_path)
    load_user_config(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
