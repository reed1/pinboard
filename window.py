from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QApplication, QMainWindow

from api import pb
from keybindings import setup_keybindings
from storage.yaml_storage import load_config, load_notes, save_notes
from undo_manager import UndoManager
from widgets.canvas import PinboardCanvas
from widgets.minimap import MinimapWidget
from widgets.text_overlay import TextOverlayWidget
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
        self._minimap = MinimapWidget(self._canvas, self)
        self._text_overlay: TextOverlayWidget | None = None

        notes = load_notes(file_path)
        self._canvas.load_notes(notes)

        self._canvas.notes_changed.connect(self._schedule_save)
        self._canvas.notes_changed.connect(self._minimap.update)
        self._canvas.viewport_changed.connect(self._minimap.update)

        setup_keybindings(self)
        self._update_title()

        self.resize(1024, 768)
        self._minimap.show()
        self._minimap.reposition()

    def _show_toast(self, message: str, timeout: int = DEFAULT_STATUS_TIMEOUT_MS) -> None:
        self._toast_manager.show_toast(message, timeout)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._toast_manager.reposition()
        self._minimap.reposition()
        if self._text_overlay:
            self._text_overlay.reposition()

    def undo(self) -> None:
        if self._canvas.is_editing():
            return
        if self._undo_manager.undo():
            self._show_toast("Undo")
            self._schedule_save()

    def redo(self) -> None:
        if self._canvas.is_editing():
            return
        if self._undo_manager.redo():
            self._show_toast("Redo")
            self._schedule_save()

    def yank(self) -> None:
        if self._canvas.is_editing():
            return
        if self._canvas.yank_selected():
            self._show_toast("Yanked")

    def cut_selected(self) -> None:
        if self._canvas.is_editing():
            return
        if self._canvas.cut_selected():
            self._show_toast("Cut")

    def delete_selected(self) -> None:
        if self._canvas.is_editing():
            return
        if self._canvas.delete_selected():
            self._show_toast("Deleted")

    def paste(self) -> None:
        if self._canvas.is_editing():
            return
        if self._canvas.paste_as_new_note():
            self._show_toast("Pasted")

    def select_next(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.select_next_note()

    def select_prev(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.select_prev_note()

    def scroll_left(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.scroll(-SCROLL_AMOUNT, 0)

    def scroll_right(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.scroll(SCROLL_AMOUNT, 0)

    def scroll_up(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.scroll(0, -SCROLL_AMOUNT)

    def scroll_down(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.scroll(0, SCROLL_AMOUNT)

    def insert_right(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.create_note_and_edit()

    def insert_below(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.create_note_below_and_edit()

    def edit(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.enter_edit_mode()

    def escape(self) -> None:
        if self._close_text_overlay():
            return
        if self._canvas.is_editing():
            self._canvas.exit_edit_mode()
        else:
            self._canvas.deselect_all()

    def reset_viewport(self) -> None:
        if self._canvas.is_editing():
            return
        self._canvas.reset_viewport()
        self._show_toast("Viewport reset")

    def show_text_overlay(self) -> None:
        if self._canvas.is_editing():
            return
        if self._text_overlay:
            return
        selected = self._canvas.get_selected_note()
        if not selected:
            return
        self._text_overlay = TextOverlayWidget(selected.text, self)
        self._text_overlay.show()
        self._text_overlay.reposition()

    def _close_text_overlay(self) -> bool:
        if not self._text_overlay:
            return False
        self._text_overlay.deleteLater()
        self._text_overlay = None
        return True

    def quit(self) -> None:
        if self._close_text_overlay():
            return
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
        save_notes(self._file_path, notes)

    def _update_title(self) -> None:
        self.setWindowTitle(f"Pinboard - {self._file_path.name}")

    def closeEvent(self, event) -> None:
        self._save_timer.stop()
        self._save()
        event.accept()


def load_user_config(window: MainWindow) -> None:
    if not USER_CONFIG_FILE.exists():
        return

    pb._initialize(window, window._canvas)

    namespace = {
        "__file__": str(USER_CONFIG_FILE),
        "pb": pb,
    }
    exec(compile(USER_CONFIG_FILE.read_text(), USER_CONFIG_FILE, "exec"), namespace)
