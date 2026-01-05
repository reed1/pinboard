from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar

from storage.yaml_storage import load_config, load_notes, save_notes
from undo_manager import UndoManager
from widgets.canvas import PinboardCanvas

CONFIG_FILE = Path(__file__).parent / "config.yaml"
SAVE_DEBOUNCE_MS = 500
DEFAULT_STATUS_TIMEOUT_MS = 2000


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

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._show_status("I/E:edit  Y:yank  P:paste  X/Del:delete  Tab:next  U:undo  Q:quit", 0)

        notes, next_id = load_notes(file_path)
        self._canvas.load_notes(notes, next_id)

        self._canvas.notes_changed.connect(self._schedule_save)

        self._setup_shortcuts()
        self._update_title()

        self.resize(1024, 768)

    def _show_status(self, message: str, timeout: int = DEFAULT_STATUS_TIMEOUT_MS) -> None:
        self._status_bar.showMessage(message, timeout)

    def _setup_shortcuts(self) -> None:
        undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        undo_shortcut.activated.connect(self._undo)

        redo_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        redo_shortcut.activated.connect(self._redo)

        redo_shortcut2 = QShortcut(QKeySequence.StandardKey.Redo, self)
        redo_shortcut2.activated.connect(self._redo)

        yank_shortcut = QShortcut(QKeySequence("Y"), self)
        yank_shortcut.activated.connect(self._yank)

        delete_shortcut = QShortcut(QKeySequence("X"), self)
        delete_shortcut.activated.connect(self._delete_selected)

        delete_shortcut2 = QShortcut(QKeySequence(Qt.Key.Key_Delete), self)
        delete_shortcut2.activated.connect(self._delete_selected)

        paste_shortcut = QShortcut(QKeySequence("P"), self)
        paste_shortcut.activated.connect(self._paste)

        tab_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Tab), self)
        tab_shortcut.activated.connect(self._select_next)

        quit_shortcut = QShortcut(QKeySequence("Q"), self)
        quit_shortcut.activated.connect(self._quit)

        undo_shortcut_u = QShortcut(QKeySequence("U"), self)
        undo_shortcut_u.activated.connect(self._undo)

        edit_shortcut_i = QShortcut(QKeySequence("I"), self)
        edit_shortcut_i.activated.connect(self._edit)

        edit_shortcut_e = QShortcut(QKeySequence("E"), self)
        edit_shortcut_e.activated.connect(self._edit)

    def _undo(self) -> None:
        if self._canvas.is_editing():
            return
        if self._undo_manager.undo():
            self._show_status("Undo")
            self._schedule_save()

    def _redo(self) -> None:
        if self._canvas.is_editing():
            return
        if self._undo_manager.redo():
            self._show_status("Redo")
            self._schedule_save()

    def _yank(self) -> None:
        if self._canvas.is_editing():
            return
        if self._canvas.yank_selected():
            self._show_status("Yanked")

    def _delete_selected(self) -> None:
        if self._canvas.is_editing():
            return
        if self._canvas.delete_selected():
            self._show_status("Deleted")

    def _paste(self) -> None:
        if self._canvas.is_editing():
            return
        if self._canvas.paste_as_new_note():
            self._show_status("Pasted")

    def _select_next(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.select_next_note()

    def _edit(self) -> None:
        if self._canvas.is_editing():
            return
        if self._canvas.enter_edit_mode():
            self._show_status("Editing (Esc to finish)")

    def _quit(self) -> None:
        if self._canvas.is_editing():
            return
        self._save_timer.stop()
        self._save()
        self._show_status("Saved")
        QApplication.quit()

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
