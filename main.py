from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut, QResizeEvent
from PySide6.QtWidgets import QApplication, QMainWindow

from api import pb
from storage.yaml_storage import load_config, load_notes, save_notes
from undo_manager import UndoManager
from widgets.canvas import PinboardCanvas
from widgets.toast import ToastManager

CONFIG_FILE = Path(__file__).parent / "config.yaml"
USER_CONFIG_FILE = Path.home() / ".config" / "pinboard" / "config.py"
SAVE_DEBOUNCE_MS = 500
DEFAULT_STATUS_TIMEOUT_MS = 2000
SCROLL_AMOUNT = 100


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

        self._toast_manager = ToastManager(self)

        notes, next_id = load_notes(file_path)
        self._canvas.load_notes(notes, next_id)

        self._canvas.notes_changed.connect(self._schedule_save)

        self._setup_shortcuts()
        self._update_title()

        self.resize(1024, 768)

    def _show_toast(self, message: str, timeout: int = DEFAULT_STATUS_TIMEOUT_MS) -> None:
        self._toast_manager.show_toast(message, timeout)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._toast_manager.reposition()

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

        ctrl_v_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        ctrl_v_shortcut.activated.connect(self._paste)

        tab_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Tab), self)
        tab_shortcut.activated.connect(self._select_next)

        j_shortcut = QShortcut(QKeySequence("J"), self)
        j_shortcut.activated.connect(self._select_next)

        l_shortcut = QShortcut(QKeySequence("L"), self)
        l_shortcut.activated.connect(self._select_next)

        shift_tab_shortcut = QShortcut(QKeySequence("Shift+Tab"), self)
        shift_tab_shortcut.activated.connect(self._select_prev)

        k_shortcut = QShortcut(QKeySequence("K"), self)
        k_shortcut.activated.connect(self._select_prev)

        h_shortcut = QShortcut(QKeySequence("H"), self)
        h_shortcut.activated.connect(self._select_prev)

        ctrl_h_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        ctrl_h_shortcut.activated.connect(self._scroll_left)

        ctrl_j_shortcut = QShortcut(QKeySequence("Ctrl+J"), self)
        ctrl_j_shortcut.activated.connect(self._scroll_down)

        ctrl_k_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        ctrl_k_shortcut.activated.connect(self._scroll_up)

        ctrl_l_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        ctrl_l_shortcut.activated.connect(self._scroll_right)

        quit_shortcut = QShortcut(QKeySequence("Q"), self)
        quit_shortcut.activated.connect(self._quit)

        undo_shortcut_u = QShortcut(QKeySequence("U"), self)
        undo_shortcut_u.activated.connect(self._undo)

        insert_shortcut = QShortcut(QKeySequence("I"), self)
        insert_shortcut.activated.connect(self._insert_right)

        insert_below_shortcut = QShortcut(QKeySequence("O"), self)
        insert_below_shortcut.activated.connect(self._insert_below)

        edit_shortcut = QShortcut(QKeySequence("E"), self)
        edit_shortcut.activated.connect(self._edit)

        esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc_shortcut.activated.connect(self._escape)

        backspace_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Backspace), self)
        backspace_shortcut.activated.connect(self._reset_viewport)

    def _undo(self) -> None:
        if self._canvas.is_editing():
            return
        if self._undo_manager.undo():
            self._show_toast("Undo")
            self._schedule_save()

    def _redo(self) -> None:
        if self._canvas.is_editing():
            return
        if self._undo_manager.redo():
            self._show_toast("Redo")
            self._schedule_save()

    def _yank(self) -> None:
        if self._canvas.is_editing():
            return
        if self._canvas.yank_selected():
            self._show_toast("Yanked")

    def _delete_selected(self) -> None:
        if self._canvas.is_editing():
            return
        if self._canvas.delete_selected():
            self._show_toast("Deleted")

    def _paste(self) -> None:
        if self._canvas.is_editing():
            return
        if self._canvas.paste_as_new_note():
            self._show_toast("Pasted")

    def _select_next(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.select_next_note()

    def _select_prev(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.select_prev_note()

    def _scroll_left(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.scroll(-SCROLL_AMOUNT, 0)

    def _scroll_right(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.scroll(SCROLL_AMOUNT, 0)

    def _scroll_up(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.scroll(0, -SCROLL_AMOUNT)

    def _scroll_down(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.scroll(0, SCROLL_AMOUNT)

    def _insert_right(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.create_note_and_edit()

    def _insert_below(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.create_note_below_and_edit()

    def _edit(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.enter_edit_mode()

    def _escape(self) -> None:
        if self._canvas.is_editing():
            self._canvas.exit_edit_mode()
        else:
            self._canvas.deselect_all()

    def _reset_viewport(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.reset_viewport()
        self._show_toast("Viewport reset")

    def _quit(self) -> None:
        if self._canvas.is_editing():
            return
        self._save_timer.stop()
        self._save()
        self._show_toast("Saved")
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


def _load_user_config(window: MainWindow) -> None:
    if not USER_CONFIG_FILE.exists():
        return

    pb._initialize(window, window._canvas)

    namespace = {
        "__file__": str(USER_CONFIG_FILE),
        "pb": pb,
    }
    exec(compile(USER_CONFIG_FILE.read_text(), USER_CONFIG_FILE, "exec"), namespace)


def main() -> None:
    if len(sys.argv) < 2:
        print("Error: YAML file path is required", file=sys.stderr)
        print("Usage: pinboard <path/to/notes.yaml>", file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])

    app = QApplication(sys.argv)
    window = MainWindow(file_path)
    _load_user_config(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
