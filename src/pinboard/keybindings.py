from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

if TYPE_CHECKING:
    from pinboard.window import MainWindow


@dataclass(frozen=True)
class Command:
    keys: str
    description: str
    callback: Callable


@dataclass(frozen=True)
class Binding:
    keys: tuple
    description: str
    action: str
    modal: bool = True


BINDINGS: list[Binding] = [
    Binding((QKeySequence.StandardKey.Undo, "U"), "Undo", "undo"),
    Binding(("Ctrl+Shift+Z", QKeySequence.StandardKey.Redo), "Redo", "redo"),
    Binding(("Y",), "Yank (copy)", "yank"),
    Binding(("D, D",), "Cut", "cut_selected"),
    Binding((Qt.Key.Key_Delete,), "Delete", "delete_selected"),
    Binding(("P", QKeySequence.StandardKey.Paste), "Paste as new note", "paste"),
    Binding((Qt.Key.Key_Tab, "J", "L"), "Select next note", "select_next"),
    Binding(("Shift+Tab", "K", "H"), "Select prev note", "select_prev"),
    Binding(("Shift+H",), "Show note text", "show_text_overlay"),
    Binding(("Ctrl+H",), "Scroll viewport left", "scroll_left"),
    Binding(("Ctrl+J",), "Scroll viewport down", "scroll_down"),
    Binding(("Ctrl+K",), "Scroll viewport up", "scroll_up"),
    Binding(("Ctrl+L",), "Scroll viewport right", "scroll_right"),
    Binding(("I",), "Insert note (right)", "insert_right"),
    Binding(("O",), "Insert note (below)", "insert_below"),
    Binding(("E",), "Edit note", "edit"),
    Binding((Qt.Key.Key_Escape,), "Close / Deselect", "escape", modal=False),
    Binding((Qt.Key.Key_Backspace,), "Reset viewport", "reset_viewport"),
    Binding(("Q",), "Quit", "quit"),
    Binding(("?",), "Show keybindings", "show_keybindings_help"),
    Binding(("Space",), "Show command palette", "show_command_palette"),
    Binding((), "Rearrange notes by id", "rearrange"),
]


def _label(keys: tuple) -> str:
    labels: list[str] = []
    for key in keys:
        text = QKeySequence(key).toString()
        if text not in labels:
            labels.append(text)
    return " / ".join(labels)


def commands(window: MainWindow) -> list[Command]:
    return [Command(_label(b.keys), b.description, getattr(window, b.action)) for b in BINDINGS]


def setup_keybindings(window: MainWindow) -> list[QShortcut]:
    modal: list[QShortcut] = []

    for binding in BINDINGS:
        callback = getattr(window, binding.action)
        for key in binding.keys:
            shortcut = QShortcut(QKeySequence(key), window)
            shortcut.activated.connect(callback)
            if binding.modal:
                modal.append(shortcut)

    return modal
