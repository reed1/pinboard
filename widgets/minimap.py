from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QBrush
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from widgets.canvas import PinboardCanvas

MINIMAP_WIDTH = 150
MINIMAP_HEIGHT = 100
MINIMAP_MARGIN = 16
MINIMAP_PADDING = 4


class MinimapWidget(QWidget):
    def __init__(self, canvas: PinboardCanvas, parent: QWidget | None = None):
        super().__init__(parent)
        self._canvas = canvas
        self.setFixedSize(MINIMAP_WIDTH, MINIMAP_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def reposition(self) -> None:
        if not self.parent():
            return
        parent_rect = self.parent().rect()
        x = parent_rect.width() - MINIMAP_WIDTH - MINIMAP_MARGIN
        y = parent_rect.height() - MINIMAP_HEIGHT - MINIMAP_MARGIN
        self.move(x, y)
        self.raise_()

    def _get_bounds(self) -> tuple[float, float, float, float]:
        notes = self._canvas._notes.values()
        viewport_rect = self._canvas.viewport().rect()
        top_left = self._canvas.mapToScene(viewport_rect.topLeft())
        bottom_right = self._canvas.mapToScene(viewport_rect.bottomRight())

        vp_min_x = top_left.x()
        vp_min_y = top_left.y()
        vp_max_x = bottom_right.x()
        vp_max_y = bottom_right.y()

        if not notes:
            return vp_min_x, vp_min_y, vp_max_x, vp_max_y

        note_min_x = min(n.pos().x() for n in notes)
        note_min_y = min(n.pos().y() for n in notes)
        note_max_x = max(n.pos().x() + n.rect().width() for n in notes)
        note_max_y = max(n.pos().y() + n.rect().height() for n in notes)

        min_x = min(vp_min_x, note_min_x)
        min_y = min(vp_min_y, note_min_y)
        max_x = max(vp_max_x, note_max_x)
        max_y = max(vp_max_y, note_max_y)

        return min_x, min_y, max_x, max_y

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor(30, 30, 30, 200))
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        draw_area = QRectF(
            MINIMAP_PADDING,
            MINIMAP_PADDING,
            MINIMAP_WIDTH - 2 * MINIMAP_PADDING,
            MINIMAP_HEIGHT - 2 * MINIMAP_PADDING,
        )

        min_x, min_y, max_x, max_y = self._get_bounds()
        world_width = max_x - min_x
        world_height = max_y - min_y

        if world_width <= 0 or world_height <= 0:
            return

        scale_x = draw_area.width() / world_width
        scale_y = draw_area.height() / world_height
        scale = min(scale_x, scale_y)

        scaled_width = world_width * scale
        scaled_height = world_height * scale
        offset_x = draw_area.x() + (draw_area.width() - scaled_width) / 2
        offset_y = draw_area.y() + (draw_area.height() - scaled_height) / 2

        def to_minimap(x: float, y: float) -> tuple[float, float]:
            return (
                offset_x + (x - min_x) * scale,
                offset_y + (y - min_y) * scale,
            )

        for note in self._canvas._notes.values():
            nx, ny = to_minimap(note.pos().x(), note.pos().y())
            nw = note.rect().width() * scale
            nh = note.rect().height() * scale
            r, g, b, a = note.color
            painter.fillRect(QRectF(nx, ny, nw, nh), QColor(r, g, b, a))
            painter.setPen(QPen(QColor(100, 100, 100), 0.5))
            painter.drawRect(QRectF(nx, ny, nw, nh))

        viewport_rect = self._canvas.viewport().rect()
        top_left = self._canvas.mapToScene(viewport_rect.topLeft())
        bottom_right = self._canvas.mapToScene(viewport_rect.bottomRight())
        vx, vy = to_minimap(top_left.x(), top_left.y())
        vw = (bottom_right.x() - top_left.x()) * scale
        vh = (bottom_right.y() - top_left.y()) * scale

        painter.setPen(QPen(QColor(100, 150, 255), 1.5))
        painter.setBrush(QBrush(QColor(100, 150, 255, 30)))
        painter.drawRect(QRectF(vx, vy, vw, vh))
