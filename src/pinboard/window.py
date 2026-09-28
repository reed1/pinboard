from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, QTimer
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QApplication, QMainWindow

from pinboard.api import pb
from pinboard.keybindings import commands, setup_keybindings
from pinboard.palette import choose_command
from pinboard.storage.yaml_storage import (
    dump_notes,
    load_config,
    load_notes,
    read_board,
    write_board,
)
from pinboard.undo_manager import UndoManager
from pinboard.widgets.canvas import PinboardCanvas
from pinboard.widgets.minimap import MinimapWidget
from pinboard.widgets.text_overlay import TextOverlayWidget
from pinboard.widgets.toast import ToastManager

USER_CONFIG_DIR = Path.home() / ".config" / "pinboard"
USER_CONFIG_YAML = USER_CONFIG_DIR / "config.yaml"
USER_CONFIG_PY = USER_CONFIG_DIR / "config.py"
SAVE_DEBOUNCE_MS = 500
RELOAD_DEBOUNCE_MS = 200
RELOAD_MAX_ATTEMPTS = 25
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

        # A change on disk is read once it has settled rather than the moment it lands: another
        # writer may be between steps, and what it has left so far is not the board.
        self._reload_timer = QTimer()
        self._reload_timer.setSingleShot(True)
        self._reload_timer.timeout.connect(self._reload)
        self._reload_attempts = 0

        self._file_watcher = QFileSystemWatcher()
        self._file_watcher.fileChanged.connect(self._on_file_changed)
        self._ensure_watching()

        config = load_config(USER_CONFIG_YAML)
        self._canvas = PinboardCanvas(config, self._undo_manager)
        self.setCentralWidget(self._canvas)

        self._toast_manager = ToastManager(self)
        self._minimap = MinimapWidget(self._canvas, self)
        self._text_overlay: TextOverlayWidget | None = None

        # The board as it last stood on disk, whether this window wrote it or read it. A change
        # event carrying this same text is this window's own save, and a save of this same text
        # has nothing to write.
        self._synced_text = file_path.read_text() if file_path.exists() else None
        notes = load_notes(file_path)
        self._canvas.load_notes(notes)

        self._canvas.notes_changed.connect(self._schedule_save)
        self._canvas.notes_changed.connect(self._minimap.update)
        self._canvas.viewport_changed.connect(self._minimap.update)

        self._modal_shortcuts = setup_keybindings(self)
        self._canvas.editing_started.connect(lambda: self._set_shortcuts_enabled(False))
        self._canvas.editing_stopped.connect(lambda: self._set_shortcuts_enabled(True))
        self._update_title()

        self.resize(1024, 768)
        self._minimap.show()
        self._minimap.reposition()

    def _set_shortcuts_enabled(self, enabled: bool) -> None:
        for s in self._modal_shortcuts:
            s.setEnabled(enabled)
        for s in pb._user_shortcuts:
            s.setEnabled(enabled)

    def _show_toast(self, message: str, timeout: int = DEFAULT_STATUS_TIMEOUT_MS) -> None:
        self._toast_manager.show_toast(message, timeout)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._toast_manager.reposition()
        self._minimap.reposition()
        if self._text_overlay:
            self._text_overlay.reposition()

    def undo(self) -> None:
        if self._undo_manager.undo():
            self._show_toast("Undo")
            self._schedule_save()

    def redo(self) -> None:
        if self._undo_manager.redo():
            self._show_toast("Redo")
            self._schedule_save()

    def yank(self) -> None:
        if self._canvas.yank_selected():
            self._show_toast("Yanked")

    def cut_selected(self) -> None:
        if self._canvas.cut_selected():
            self._show_toast("Cut")

    def delete_selected(self) -> None:
        if self._canvas.delete_selected():
            self._show_toast("Deleted")

    def paste(self) -> None:
        if self._canvas.paste_as_new_note():
            self._show_toast("Pasted")

    def select_next(self) -> None:
        self._close_text_overlay()
        self._canvas.select_next_note()

    def select_prev(self) -> None:
        self._close_text_overlay()
        self._canvas.select_prev_note()

    def scroll_left(self) -> None:
        self._canvas.scroll(-SCROLL_AMOUNT, 0)

    def scroll_right(self) -> None:
        self._canvas.scroll(SCROLL_AMOUNT, 0)

    def scroll_up(self) -> None:
        self._canvas.scroll(0, -SCROLL_AMOUNT)

    def scroll_down(self) -> None:
        self._canvas.scroll(0, SCROLL_AMOUNT)

    def insert_right(self) -> None:
        self._canvas.create_note_and_edit()

    def insert_below(self) -> None:
        self._canvas.create_note_below_and_edit()

    def edit(self) -> None:
        self._canvas.enter_edit_mode()

    def escape(self) -> None:
        if self._close_text_overlay():
            return
        if self._canvas.is_editing():
            self._canvas.exit_edit_mode()
        else:
            self._canvas.deselect_all()

    def rearrange(self) -> None:
        if self._canvas.rearrange_notes():
            self._show_toast("Rearranged")

    def reset_viewport(self) -> None:
        self._canvas.reset_viewport()
        self._show_toast("Viewport reset")

    def show_keybindings_help(self) -> None:
        if self._text_overlay:
            return
        bound = [c for c in commands(self) if c.keys]
        key_col_width = max(len(c.keys) for c in bound)
        lines = ["KEYBINDINGS", ""]
        for command in bound:
            lines.append(f"  {command.keys.ljust(key_col_width)}   {command.description}")
        if pb._commands:
            key_col_width = max(key_col_width, max(len(c.keys) for c in pb._commands))
            lines += ["", "USER KEYBINDINGS", ""]
            for command in pb._commands:
                lines.append(f"  {command.keys.ljust(key_col_width)}   {command.description}")
        self._text_overlay = TextOverlayWidget("\n".join(lines), self)
        self._text_overlay.show()
        self._text_overlay.reposition()

    def show_command_palette(self) -> None:
        self._close_text_overlay()
        command = choose_command(commands(self) + pb._commands)
        if command is None:
            return
        # Let the window settle back in before the action runs: rofi held the
        # keyboard grab until it exited.
        QTimer.singleShot(0, command.callback)

    def show_text_overlay(self) -> None:
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
        self._flush()
        self._show_toast("Saved")
        QApplication.quit()

    def _schedule_save(self) -> None:
        self._save_timer.start(SAVE_DEBOUNCE_MS)

    def _save(self) -> None:
        text = dump_notes(self._canvas.get_notes())
        if text == self._synced_text:
            return
        write_board(self._file_path, text)
        self._synced_text = text
        self._ensure_watching()

    def _flush(self) -> None:
        """A change on disk still waiting to be read goes in first, so saving on the way out does
        not write the board back over it."""
        self._save_timer.stop()
        if self._reload_timer.isActive():
            self._reload_timer.stop()
            self._reload()
        self._save()

    def _on_file_changed(self, _path: str) -> None:
        self._reload_attempts = 0
        self._reload_timer.start(RELOAD_DEBOUNCE_MS)

    def _reload(self) -> None:
        self._ensure_watching()
        board = read_board(self._file_path)
        if board is None:
            self._reload_attempts += 1
            if self._reload_attempts < RELOAD_MAX_ATTEMPTS:
                self._reload_timer.start(RELOAD_DEBOUNCE_MS)
            else:
                self._show_toast("Board file unreadable, keeping the notes shown")
            return

        text, notes = board
        if text == self._synced_text:
            return
        self._synced_text = text

        if self._canvas.is_editing():
            self._canvas.exit_edit_mode()
        selected = self._canvas.get_selected_note()
        selected_id = selected.note_id if selected else None
        self._canvas.load_notes(notes)
        if selected_id is not None and selected_id not in self._canvas._notes:
            self._canvas.deselect_all()
        elif selected_id is not None and selected_id in self._canvas._notes:
            self._canvas._scene.clearSelection()
            self._canvas._notes[selected_id].setSelected(True)
        self._undo_manager.clear()
        self._show_toast("Reloaded")

    def _ensure_watching(self) -> None:
        """A replaced file is a new inode, and the watch on the old one goes with it."""
        path = str(self._file_path)
        if self._file_path.exists() and path not in self._file_watcher.files():
            self._file_watcher.addPath(path)

    def _update_title(self) -> None:
        self.setWindowTitle(f"Pinboard - {self._file_path.name}")

    def closeEvent(self, event) -> None:
        self._flush()
        event.accept()


def load_user_config(window: MainWindow) -> None:
    if not USER_CONFIG_PY.exists():
        return

    pb._initialize(window, window._canvas)

    namespace = {
        "__file__": str(USER_CONFIG_PY),
        "pb": pb,
    }
    exec(compile(USER_CONFIG_PY.read_text(), USER_CONFIG_PY, "exec"), namespace)
