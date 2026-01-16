from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPropertyAnimation, QTimer, Qt, QEasingCurve
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QGraphicsOpacityEffect

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

DEFAULT_TIMEOUT_MS = 2000
FADE_DURATION_MS = 200
TOAST_SPACING = 8
TOAST_MARGIN = 16


class ToastWidget(QFrame):
    def __init__(
        self,
        message: str,
        timeout_ms: int,
        manager: ToastManager,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._manager = manager
        self._timeout_ms = timeout_ms

        self.setStyleSheet(
            """
            ToastWidget {
                background-color: rgba(20, 20, 20, 240);
                border-radius: 6px;
                padding: 8px 12px;
            }
            QLabel {
                color: white;
                font-size: 13px;
            }
        """
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        self._label = QLabel(message)
        self._label.setWordWrap(True)
        layout.addWidget(self._label)

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._fade_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_animation.setDuration(FADE_DURATION_MS)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._fade_animation.finished.connect(self._on_fade_finished)

        self._dismiss_timer = QTimer(self)
        self._dismiss_timer.setSingleShot(True)
        self._dismiss_timer.timeout.connect(self._start_fade_out)

        self._fading_out = False

        self.adjustSize()
        self.setMinimumWidth(150)
        self.setMaximumWidth(300)

    def start(self) -> None:
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.start()
        if self._timeout_ms > 0:
            self._dismiss_timer.start(self._timeout_ms)

    def _start_fade_out(self) -> None:
        if self._fading_out:
            return
        self._fading_out = True
        self._dismiss_timer.stop()
        self._fade_animation.setStartValue(self._opacity_effect.opacity())
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.start()

    def _on_fade_finished(self) -> None:
        if self._fading_out:
            self._manager.remove_toast(self)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._start_fade_out()
        event.accept()


class ToastManager:
    def __init__(self, parent: QWidget):
        self._parent = parent
        self._toasts: list[ToastWidget] = []

    def show_toast(self, message: str, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
        toast = ToastWidget(message, timeout_ms, self, self._parent)
        self._toasts.append(toast)
        toast.show()
        toast.start()
        self._reposition_toasts()

    def remove_toast(self, toast: ToastWidget) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
            toast.deleteLater()
            self._reposition_toasts()

    def _reposition_toasts(self) -> None:
        parent_rect = self._parent.rect()
        y_offset = TOAST_MARGIN

        for toast in reversed(self._toasts):
            toast.adjustSize()
            x = parent_rect.width() - toast.width() - TOAST_MARGIN
            y = parent_rect.height() - toast.height() - y_offset
            toast.move(x, y)
            toast.raise_()
            y_offset += toast.height() + TOAST_SPACING

    def reposition(self) -> None:
        self._reposition_toasts()
