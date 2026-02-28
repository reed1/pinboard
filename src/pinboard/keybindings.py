from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

if TYPE_CHECKING:
    from pinboard.window import MainWindow

KEYBINDING_HELP: list[tuple[str, str]] = [
    ("Ctrl+Z / U", "Undo"),
    ("Ctrl+Shift+Z", "Redo"),
    ("Y", "Yank (copy)"),
    ("D, D", "Cut"),
    ("Del", "Delete"),
    ("P / Ctrl+V", "Paste as new note"),
    ("Tab / J / L", "Select next note"),
    ("Shift+Tab / K / H", "Select prev note"),
    ("Shift+H", "Show note text"),
    ("Ctrl+H/J/K/L", "Scroll viewport"),
    ("I", "Insert note (right)"),
    ("O", "Insert note (below)"),
    ("E", "Edit note"),
    ("Esc", "Close / Deselect"),
    ("Backspace", "Reset viewport"),
    ("Q", "Quit"),
    ("?", "Show keybindings"),
]


def _shortcut(key, window: MainWindow, callback) -> QShortcut:
    s = QShortcut(QKeySequence(key), window)
    s.activated.connect(callback)
    return s


def setup_keybindings(window: MainWindow) -> list[QShortcut]:
    modal: list[QShortcut] = []

    modal.append(_shortcut(QKeySequence.StandardKey.Undo, window, window.undo))
    modal.append(_shortcut("Ctrl+Shift+Z", window, window.redo))
    modal.append(_shortcut(QKeySequence.StandardKey.Redo, window, window.redo))
    modal.append(_shortcut("Y", window, window.yank))
    modal.append(_shortcut(Qt.Key.Key_Delete, window, window.delete_selected))
    modal.append(_shortcut("D, D", window, window.cut_selected))
    modal.append(_shortcut("P", window, window.paste))
    modal.append(_shortcut(QKeySequence.StandardKey.Paste, window, window.paste))
    modal.append(_shortcut(Qt.Key.Key_Tab, window, window.select_next))
    modal.append(_shortcut("J", window, window.select_next))
    modal.append(_shortcut("L", window, window.select_next))
    modal.append(_shortcut("Shift+Tab", window, window.select_prev))
    modal.append(_shortcut("K", window, window.select_prev))
    modal.append(_shortcut("H", window, window.select_prev))
    modal.append(_shortcut("Shift+H", window, window.show_text_overlay))
    modal.append(_shortcut("Ctrl+H", window, window.scroll_left))
    modal.append(_shortcut("Ctrl+J", window, window.scroll_down))
    modal.append(_shortcut("Ctrl+K", window, window.scroll_up))
    modal.append(_shortcut("Ctrl+L", window, window.scroll_right))
    modal.append(_shortcut("Q", window, window.quit))
    modal.append(_shortcut("U", window, window.undo))
    modal.append(_shortcut("I", window, window.insert_right))
    modal.append(_shortcut("O", window, window.insert_below))
    modal.append(_shortcut("E", window, window.edit))
    modal.append(_shortcut(Qt.Key.Key_Backspace, window, window.reset_viewport))
    modal.append(_shortcut("?", window, window.show_keybindings_help))

    # Escape is always active (not modal)
    _shortcut(Qt.Key.Key_Escape, window, window.escape)

    return modal
