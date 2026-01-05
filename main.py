from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QMainWindow

from storage.yaml_storage import load_config, load_notes, save_notes
from undo_manager import UndoManager
from widgets.canvas import PinboardCanvas

CONFIG_FILE = Path(__file__).parent / "config.yaml"
SAVE_DEBOUNCE_MS = 500


class MainWindow(QMainWindow):
    def __init__(self, file_path: Path):
        super().__init__()

        self._file_path = file_path
        self._undo_manager = UndoManager()
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save)

        config = load_config(CONFIG_FILE)
        self._canvas = PinboardCanvas(config, self._undo_manager)
        self.setCentralWidget(self._canvas)

        notes, next_id = load_notes(file_path)
        self._canvas.load_notes(notes, next_id)

        self._canvas.notes_changed.connect(self._schedule_save)

        self._setup_shortcuts()
        self._update_title()

        self.resize(1024, 768)

    def _setup_shortcuts(self) -> None:
        undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        undo_shortcut.activated.connect(self._undo)

        redo_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        redo_shortcut.activated.connect(self._redo)

        redo_shortcut2 = QShortcut(QKeySequence.StandardKey.Redo, self)
        redo_shortcut2.activated.connect(self._redo)

    def _undo(self) -> None:
        if self._undo_manager.undo():
            self._schedule_save()

    def _redo(self) -> None:
        if self._undo_manager.redo():
            self._schedule_save()

    def _schedule_save(self) -> None:
        self._save_timer.start(SAVE_DEBOUNCE_MS)

    def _save(self) -> None:
        notes = self._canvas.get_notes()
        next_id = self._canvas.get_next_id()
        save_notes(self._file_path, notes, next_id)

    def _update_title(self) -> None:
        self.setWindowTitle(f"Pinboard - {self._file_path.name}")

    def closeEvent(self, event) -> None:
        self._save_timer.stop()
        self._save()
        event.accept()


def main() -> None:
    if len(sys.argv) < 2:
        print("Error: YAML file path is required", file=sys.stderr)
        print("Usage: pinboard <path/to/notes.yaml>", file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])

    app = QApplication(sys.argv)
    window = MainWindow(file_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
