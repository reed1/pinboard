from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QTimer
from PySide6.QtGui import QKeySequence, QShortcut

from pinboard.keybindings import Command

if TYPE_CHECKING:
    from pinboard.widgets.canvas import PinboardCanvas
    from pinboard.window import MainWindow

DEFAULT_TOAST_TIMEOUT_MS = 2000


class PinboardAPI:
    def __init__(self):
        self._window: MainWindow | None = None
        self._canvas: PinboardCanvas | None = None
        self._pending_keybindings: list[tuple[str, Callable, str | None]] = []
        self._commands: list[Command] = []
        self._user_shortcuts: list[QShortcut] = []

    def _initialize(self, window: MainWindow, canvas: PinboardCanvas) -> None:
        self._window = window
        self._canvas = canvas
        for key, callback, description in self._pending_keybindings:
            self._register_keybinding(key, callback, description)
        self._pending_keybindings.clear()

    @property
    def window(self) -> MainWindow:
        if self._window is None:
            raise RuntimeError("Pinboard API not initialized yet")
        return self._window

    @property
    def canvas(self) -> PinboardCanvas:
        if self._canvas is None:
            raise RuntimeError("Pinboard API not initialized yet")
        return self._canvas

    def toast(self, message: str, timeout: int = DEFAULT_TOAST_TIMEOUT_MS) -> None:
        if self._window is None:
            raise RuntimeError("Pinboard API not initialized yet")
        self._window._show_toast(message, timeout)

    def add_keybinding(self, key: str, callback: Callable, description: str | None = None) -> None:
        if self._window is None:
            self._pending_keybindings.append((key, callback, description))
        else:
            self._register_keybinding(key, callback, description)

    def _register_keybinding(self, key: str, callback: Callable, description: str | None) -> None:
        shortcut = QShortcut(QKeySequence(key), self._window)
        shortcut.activated.connect(callback)
        self._user_shortcuts.append(shortcut)
        if description is None:
            name = getattr(callback, "__name__", None) or "?"
            description = name.replace("_", " ")
        self._commands.append(Command(key, description, callback))

    def call_later(self, callback: Callable, delay_ms: int = 0) -> None:
        QTimer.singleShot(delay_ms, callback)

    def get_file_path(self) -> str:
        if self._window is None:
            raise RuntimeError("Pinboard API not initialized yet")
        return str(self._window._file_path)


pb = PinboardAPI()
