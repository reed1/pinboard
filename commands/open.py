from __future__ import annotations

import argparse
import sys


def run(args: argparse.Namespace) -> None:
    from PySide6.QtWidgets import QApplication

    from window import MainWindow, load_user_config

    app = QApplication(sys.argv)
    window = MainWindow(args.file)
    load_user_config(window)
    window.show()
    sys.exit(app.exec())
