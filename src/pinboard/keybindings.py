from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

if TYPE_CHECKING:
    from pinboard.window import MainWindow


def setup_keybindings(window: MainWindow) -> None:
    undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, window)
    undo_shortcut.activated.connect(window.undo)

    redo_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), window)
    redo_shortcut.activated.connect(window.redo)

    redo_shortcut2 = QShortcut(QKeySequence.StandardKey.Redo, window)
    redo_shortcut2.activated.connect(window.redo)

    yank_shortcut = QShortcut(QKeySequence("Y"), window)
    yank_shortcut.activated.connect(window.yank)

    cut_shortcut = QShortcut(QKeySequence("X"), window)
    cut_shortcut.activated.connect(window.cut_selected)

    delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), window)
    delete_shortcut.activated.connect(window.delete_selected)

    paste_shortcut = QShortcut(QKeySequence("P"), window)
    paste_shortcut.activated.connect(window.paste)

    ctrl_v_shortcut = QShortcut(QKeySequence.StandardKey.Paste, window)
    ctrl_v_shortcut.activated.connect(window.paste)

    tab_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Tab), window)
    tab_shortcut.activated.connect(window.select_next)

    j_shortcut = QShortcut(QKeySequence("J"), window)
    j_shortcut.activated.connect(window.select_next)

    l_shortcut = QShortcut(QKeySequence("L"), window)
    l_shortcut.activated.connect(window.select_next)

    shift_tab_shortcut = QShortcut(QKeySequence("Shift+Tab"), window)
    shift_tab_shortcut.activated.connect(window.select_prev)

    k_shortcut = QShortcut(QKeySequence("K"), window)
    k_shortcut.activated.connect(window.select_prev)

    h_shortcut = QShortcut(QKeySequence("H"), window)
    h_shortcut.activated.connect(window.select_prev)

    shift_h_shortcut = QShortcut(QKeySequence("Shift+H"), window)
    shift_h_shortcut.activated.connect(window.show_text_overlay)

    ctrl_h_shortcut = QShortcut(QKeySequence("Ctrl+H"), window)
    ctrl_h_shortcut.activated.connect(window.scroll_left)

    ctrl_j_shortcut = QShortcut(QKeySequence("Ctrl+J"), window)
    ctrl_j_shortcut.activated.connect(window.scroll_down)

    ctrl_k_shortcut = QShortcut(QKeySequence("Ctrl+K"), window)
    ctrl_k_shortcut.activated.connect(window.scroll_up)

    ctrl_l_shortcut = QShortcut(QKeySequence("Ctrl+L"), window)
    ctrl_l_shortcut.activated.connect(window.scroll_right)

    quit_shortcut = QShortcut(QKeySequence("Q"), window)
    quit_shortcut.activated.connect(window.quit)

    undo_shortcut_u = QShortcut(QKeySequence("U"), window)
    undo_shortcut_u.activated.connect(window.undo)

    insert_shortcut = QShortcut(QKeySequence("I"), window)
    insert_shortcut.activated.connect(window.insert_right)

    insert_below_shortcut = QShortcut(QKeySequence("O"), window)
    insert_below_shortcut.activated.connect(window.insert_below)

    edit_shortcut = QShortcut(QKeySequence("E"), window)
    edit_shortcut.activated.connect(window.edit)

    esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), window)
    esc_shortcut.activated.connect(window.escape)

    backspace_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Backspace), window)
    backspace_shortcut.activated.connect(window.reset_viewport)
