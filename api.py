from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from PySide6.QtGui import QKeySequence, QShortcut

if TYPE_CHECKING:
    from widgets.canvas import PinboardCanvas
    from main import MainWindow

DEFAULT_TOAST_TIMEOUT_MS = 2000


class PinboardAPI:
    def __init__(self):
        self._window: MainWindow | None = None
        self._canvas: PinboardCanvas | None = None
        self._pending_keybindings: list[tuple[str, Callable]] = []

    def _initialize(self, window: MainWindow, canvas: PinboardCanvas) -> None:
        self._window = window
        self._canvas = canvas
        for key, callback in self._pending_keybindings:
            self._register_keybinding(key, callback)
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

    def add_keybinding(self, key: str, callback: Callable) -> None:
        if self._window is None:
            self._pending_keybindings.append((key, callback))
        else:
            self._register_keybinding(key, callback)

    def _register_keybinding(self, key: str, callback: Callable) -> None:
        shortcut = QShortcut(QKeySequence(key), self._window)
        shortcut.activated.connect(callback)

    def get_file_path(self) -> str:
        if self._window is None:
            raise RuntimeError("Pinboard API not initialized yet")
        return str(self._window._file_path)


pb = PinboardAPI()
