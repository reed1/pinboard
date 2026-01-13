from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

PADDING = 16


class TextOverlayWidget(QFrame):
    def __init__(
        self,
        text: str,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.setStyleSheet(
            """
            TextOverlayWidget {
                background-color: rgb(30, 30, 30);
                border: 2px solid rgb(0, 150, 200);
            }
            QLabel {
                color: rgb(200, 200, 200);
                font-family: monospace;
                font-size: 22px;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)

        self._label = QLabel(text)
        self._label.setWordWrap(True)
        self._label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self._label)

    def reposition(self) -> None:
        parent = self.parentWidget()
        if not parent:
            return

        parent_rect = parent.rect()
        target_width = int(parent_rect.width() * 0.8)
        self.setFixedWidth(target_width)
        self.adjustSize()

        x = (parent_rect.width() - self.width()) // 2
        y = (parent_rect.height() - self.height()) // 2
        self.move(x, y)
        self.raise_()
