from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal, QObject
from PySide6.QtGui import QBrush, QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem

MIN_WIDTH = 100
MIN_HEIGHT = 60
HANDLE_SIZE = 10
PADDING = 8
SELECTION_BORDER_WIDTH = 3
SELECTION_BORDER_COLOR = (0, 150, 255, 255)


class NoteSignals(QObject):
    moved = Signal(int, float, float, float, float)  # id, old_x, old_y, new_x, new_y
    resized = Signal(int, float, float, float, float)  # id, old_w, old_h, new_w, new_h
    text_changed = Signal(int, str, str)  # id, old_text, new_text
    changed = Signal()
    edit_finished = Signal()


class NoteItem(QGraphicsRectItem):
    def __init__(
        self,
        note_id: int,
        x: float,
        y: float,
        width: float,
        height: float,
        text: str,
        order: int,
        color: tuple[int, int, int, int],
    ):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)

        self.note_id = note_id
        self.text = text
        self.order = order
        self.color = color

        self.signals = NoteSignals()

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        self.setZValue(order)

        self._resizing = False
        self._resize_corner: str | None = None
        self._drag_start_pos = None
        self._drag_start_rect = None
        self._move_start_pos = None

        self._editing = False
        self._text_item: QGraphicsTextItem | None = None
        self._edit_start_text: str = ""

        self._update_appearance()

    def _update_appearance(self) -> None:
        r, g, b, a = self.color
        self.setBrush(QBrush(QColor(r, g, b, a)))
        self.setPen(QPen(QColor(100, 100, 100), 1))

    def set_color(self, color: tuple[int, int, int, int]) -> None:
        self.color = color
        self._update_appearance()
        self.update()

    def set_order(self, order: int) -> None:
        self.order = order
        self.setZValue(order)

    def set_text(self, text: str) -> None:
        self.text = text
        self.update()

    def paint(self, painter: QPainter, option, widget=None) -> None:
        super().paint(painter, option, widget)

        rect = self.rect()

        if not self._editing:
            text_rect = rect.adjusted(PADDING, PADDING, -PADDING, -PADDING)

            font = QFont("Sans", 10)
            painter.setFont(font)
            painter.setPen(QPen(QColor(30, 30, 30)))

            metrics = QFontMetrics(font)
            elided_lines = []
            lines = self.text.split("\n")
            available_height = text_rect.height()
            line_height = metrics.lineSpacing()
            max_lines = max(1, int(available_height / line_height))

            for i, line in enumerate(lines):
                if i >= max_lines:
                    break
                if i == max_lines - 1 and len(lines) > max_lines:
                    elided = metrics.elidedText(line + "...", Qt.TextElideMode.ElideRight, int(text_rect.width()))
                else:
                    elided = metrics.elidedText(line, Qt.TextElideMode.ElideRight, int(text_rect.width()))
                elided_lines.append(elided)

            y_offset = text_rect.top()
            for line in elided_lines:
                painter.drawText(
                    int(text_rect.left()),
                    int(y_offset + metrics.ascent()),
                    line,
                )
                y_offset += line_height

        if self.isSelected():
            r, g, b, a = SELECTION_BORDER_COLOR
            selection_pen = QPen(QColor(r, g, b, a), SELECTION_BORDER_WIDTH)
            painter.setPen(selection_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            inset = SELECTION_BORDER_WIDTH / 2
            painter.drawRect(rect.adjusted(inset, inset, -inset, -inset))

            for corner in ["tl", "tr", "bl", "br"]:
                handle_rect = self._get_handle_rect(corner)
                painter.fillRect(handle_rect, QColor(80, 80, 80))

    def _get_handle_rect(self, corner: str) -> QRectF:
        rect = self.rect()
        if corner == "tl":
            return QRectF(rect.left(), rect.top(), HANDLE_SIZE, HANDLE_SIZE)
        if corner == "tr":
            return QRectF(rect.right() - HANDLE_SIZE, rect.top(), HANDLE_SIZE, HANDLE_SIZE)
        if corner == "bl":
            return QRectF(rect.left(), rect.bottom() - HANDLE_SIZE, HANDLE_SIZE, HANDLE_SIZE)
        if corner == "br":
            return QRectF(
                rect.right() - HANDLE_SIZE,
                rect.bottom() - HANDLE_SIZE,
                HANDLE_SIZE,
                HANDLE_SIZE,
            )
        raise ValueError(f"Unknown corner: {corner}")

    def _get_corner_at(self, pos) -> str | None:
        for corner in ["tl", "tr", "bl", "br"]:
            if self._get_handle_rect(corner).contains(pos):
                return corner
        return None

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.isSelected():
            corner = self._get_corner_at(event.pos())
            if corner:
                self._resizing = True
                self._resize_corner = corner
                self._drag_start_pos = event.pos()
                self._drag_start_rect = self.rect()
                event.accept()
                return

        self._move_start_pos = self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._resizing and self._drag_start_rect:
            delta = event.pos() - self._drag_start_pos
            new_rect = QRectF(self._drag_start_rect)

            if self._resize_corner == "br":
                new_rect.setWidth(max(MIN_WIDTH, self._drag_start_rect.width() + delta.x()))
                new_rect.setHeight(max(MIN_HEIGHT, self._drag_start_rect.height() + delta.y()))
            elif self._resize_corner == "bl":
                new_width = max(MIN_WIDTH, self._drag_start_rect.width() - delta.x())
                if new_width > MIN_WIDTH:
                    self.setX(self.x() + delta.x())
                new_rect.setWidth(new_width)
                new_rect.setHeight(max(MIN_HEIGHT, self._drag_start_rect.height() + delta.y()))
            elif self._resize_corner == "tr":
                new_rect.setWidth(max(MIN_WIDTH, self._drag_start_rect.width() + delta.x()))
                new_height = max(MIN_HEIGHT, self._drag_start_rect.height() - delta.y())
                if new_height > MIN_HEIGHT:
                    self.setY(self.y() + delta.y())
                new_rect.setHeight(new_height)
            elif self._resize_corner == "tl":
                new_width = max(MIN_WIDTH, self._drag_start_rect.width() - delta.x())
                new_height = max(MIN_HEIGHT, self._drag_start_rect.height() - delta.y())
                if new_width > MIN_WIDTH:
                    self.setX(self.x() + delta.x())
                if new_height > MIN_HEIGHT:
                    self.setY(self.y() + delta.y())
                new_rect.setWidth(new_width)
                new_rect.setHeight(new_height)

            self.setRect(0, 0, new_rect.width(), new_rect.height())
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._resizing and self._drag_start_rect:
            old_w = self._drag_start_rect.width()
            old_h = self._drag_start_rect.height()
            new_w = self.rect().width()
            new_h = self.rect().height()
            if old_w != new_w or old_h != new_h:
                self.signals.resized.emit(self.note_id, old_w, old_h, new_w, new_h)
                self.signals.changed.emit()
            self._resizing = False
            self._resize_corner = None
            self._drag_start_pos = None
            self._drag_start_rect = None
            event.accept()
            return

        if self._move_start_pos is not None:
            old_pos = self._move_start_pos
            new_pos = self.pos()
            if old_pos != new_pos:
                self.signals.moved.emit(self.note_id, old_pos.x(), old_pos.y(), new_pos.x(), new_pos.y())
                self.signals.changed.emit()
            self._move_start_pos = None

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.enter_edit_mode()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def is_editing(self) -> bool:
        return self._editing

    def enter_edit_mode(self) -> None:
        if self._editing:
            return

        self._editing = True
        self._edit_start_text = self.text

        self._text_item = QGraphicsTextItem(self)
        self._text_item.setPlainText(self.text)
        self._text_item.setFont(QFont("Sans", 10))
        self._text_item.setDefaultTextColor(QColor(30, 30, 30))
        self._text_item.setPos(PADDING, PADDING)
        self._text_item.setTextWidth(self.rect().width() - PADDING * 2)
        self._text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self._text_item.setFocus()

        cursor = self._text_item.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self._text_item.setTextCursor(cursor)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.update()

    def exit_edit_mode(self) -> None:
        if not self._editing or not self._text_item:
            return

        new_text = self._text_item.toPlainText()

        self._text_item.setParentItem(None)
        if self.scene():
            self.scene().removeItem(self._text_item)
        self._text_item = None
        self._editing = False

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

        if new_text != self._edit_start_text:
            self.text = new_text
            self.signals.text_changed.emit(self.note_id, self._edit_start_text, new_text)
            self.signals.changed.emit()

        self._edit_start_text = ""
        self.update()
        self.signals.edit_finished.emit()

    def hoverMoveEvent(self, event) -> None:
        if self.isSelected():
            corner = self._get_corner_at(event.pos())
            if corner in ("tl", "br"):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif corner in ("tr", "bl"):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)
