from __future__ import annotations

import random
from typing import Callable

from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QAction, QColor, QPainter, QWheelEvent
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMenu

from models.note import Note
from storage.yaml_storage import Config
from undo_manager import (
    ChangeColorAction,
    ChangeOrderAction,
    CreateNoteAction,
    DeleteNoteAction,
    EditTextAction,
    MoveNoteAction,
    ResizeNoteAction,
    UndoManager,
)
from widgets.note_item import NoteItem


class PinboardCanvas(QGraphicsView):
    notes_changed = Signal()

    def __init__(
        self,
        config: Config,
        undo_manager: UndoManager,
    ):
        super().__init__()

        self._scene = QGraphicsScene()
        self._scene.setSceneRect(-5000, -5000, 25000, 25000)
        r, g, b, a = config.canvas_background
        self._scene.setBackgroundBrush(QColor(r, g, b, a))
        self.setScene(self._scene)

        self._config = config
        self._undo_manager = undo_manager
        self._notes: dict[int, NoteItem] = {}
        self._next_id = 1

        self._panning = False
        self._pan_start: QPointF | None = None

        self.setRenderHints(
            self.renderHints() | QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._viewport_initialized = False

    def paintEvent(self, event) -> None:
        if not self._viewport_initialized:
            self._viewport_initialized = True
            self.horizontalScrollBar().setValue(0)
            self.verticalScrollBar().setValue(0)
        super().paintEvent(event)

    def reset_viewport(self) -> None:
        self.resetTransform()
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)

    def scroll(self, dx: int, dy: int) -> None:
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + dx)
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + dy)

    def load_notes(self, notes: list[Note], next_id: int) -> None:
        self._scene.clear()
        self._notes.clear()
        self._next_id = next_id

        for note in sorted(notes, key=lambda n: n.order):
            self._add_note_item(note, record_undo=False)

    def get_notes(self) -> list[Note]:
        return [
            Note(
                id=item.note_id,
                x=item.pos().x(),
                y=item.pos().y(),
                width=item.rect().width(),
                height=item.rect().height(),
                text=item.text,
                order=item.order,
                color=item.color,
            )
            for item in self._notes.values()
        ]

    def get_next_id(self) -> int:
        return self._next_id

    def _add_note_item(self, note: Note, record_undo: bool = True) -> NoteItem:
        item = NoteItem(
            note_id=note.id,
            x=note.x,
            y=note.y,
            width=note.width,
            height=note.height,
            text=note.text,
            order=note.order,
            color=note.color,
            text_color=self._config.text_color,
            font_family=self._config.font_family,
            font_size=self._config.font_size,
        )
        self._scene.addItem(item)
        self._notes[note.id] = item

        item.signals.moved.connect(self._on_note_moved)
        item.signals.resized.connect(self._on_note_resized)
        item.signals.text_changed.connect(self._on_note_text_changed)
        item.signals.changed.connect(self.notes_changed.emit)

        if record_undo:
            action = CreateNoteAction(
                note_id=note.id,
                delete_callback=self._delete_note_by_id,
                recreate_callback=lambda n: self._add_note_item(n, record_undo=False),
                note_data=note,
            )
            self._undo_manager.push(action)

        return item

    def _calculate_position_right(self) -> tuple[float, float]:
        padding = self._config.padding
        selected = self.get_selected_note()
        if selected:
            return (selected.pos().x() + selected.rect().width() + padding, selected.pos().y())
        if not self._notes:
            return (padding, padding)
        max_id = max(self._notes.keys())
        last_note = self._notes[max_id]
        return (last_note.pos().x() + last_note.rect().width() + padding, last_note.pos().y())

    def _calculate_position_below(self) -> tuple[float, float]:
        padding = self._config.padding
        selected = self.get_selected_note()
        if selected:
            return (selected.pos().x(), selected.pos().y() + selected.rect().height() + padding)
        if not self._notes:
            return (padding, padding)
        max_id = max(self._notes.keys())
        last_note = self._notes[max_id]
        return (last_note.pos().x(), last_note.pos().y() + last_note.rect().height() + padding)

    def _create_note_at(self, x: float, y: float) -> NoteItem:
        color = random.choice(self._config.palette)
        order = self._get_max_order() + 1

        note = Note(
            id=self._next_id,
            x=x,
            y=y,
            width=self._config.default_width,
            height=self._config.default_height,
            text="",
            order=order,
            color=color,
        )
        self._next_id += 1
        item = self._add_note_item(note, record_undo=True)
        self.notes_changed.emit()
        return item

    def _delete_note_by_id(self, note_id: int) -> None:
        if note_id in self._notes:
            item = self._notes.pop(note_id)
            self._scene.removeItem(item)

    def _delete_note(self, item: NoteItem) -> None:
        note_data = Note(
            id=item.note_id,
            x=item.pos().x(),
            y=item.pos().y(),
            width=item.rect().width(),
            height=item.rect().height(),
            text=item.text,
            order=item.order,
            color=item.color,
        )

        action = DeleteNoteAction(
            note_data=note_data,
            recreate_callback=lambda n: self._add_note_item(n, record_undo=False),
            delete_callback=self._delete_note_by_id,
        )
        self._undo_manager.push(action)

        self._delete_note_by_id(item.note_id)
        self.notes_changed.emit()

    def _get_max_order(self) -> int:
        if not self._notes:
            return 0
        return max(item.order for item in self._notes.values())

    def _get_min_order(self) -> int:
        if not self._notes:
            return 0
        return min(item.order for item in self._notes.values())

    def _bring_to_front(self, item: NoteItem) -> None:
        old_order = item.order
        new_order = self._get_max_order() + 1
        if old_order == new_order:
            return

        action = ChangeOrderAction(
            note_id=item.note_id,
            old_order=old_order,
            new_order=new_order,
            update_callback=self._update_note_order,
        )
        self._undo_manager.push(action)

        item.set_order(new_order)
        self.notes_changed.emit()

    def _send_to_back(self, item: NoteItem) -> None:
        old_order = item.order
        new_order = self._get_min_order() - 1
        if old_order == new_order:
            return

        action = ChangeOrderAction(
            note_id=item.note_id,
            old_order=old_order,
            new_order=new_order,
            update_callback=self._update_note_order,
        )
        self._undo_manager.push(action)

        item.set_order(new_order)
        self.notes_changed.emit()

    def _change_color(self, item: NoteItem, new_color: tuple[int, int, int, int]) -> None:
        old_color = item.color
        if old_color == new_color:
            return

        action = ChangeColorAction(
            note_id=item.note_id,
            old_color=old_color,
            new_color=new_color,
            update_callback=self._update_note_color,
        )
        self._undo_manager.push(action)

        item.set_color(new_color)
        self.notes_changed.emit()

    def _update_note_order(self, note_id: int, order: int) -> None:
        if note_id in self._notes:
            self._notes[note_id].set_order(order)
            self.notes_changed.emit()

    def _update_note_color(self, note_id: int, color: tuple[int, int, int, int]) -> None:
        if note_id in self._notes:
            self._notes[note_id].set_color(color)
            self.notes_changed.emit()

    def _update_note_position(self, note_id: int, x: float, y: float) -> None:
        if note_id in self._notes:
            self._notes[note_id].setPos(x, y)
            self.notes_changed.emit()

    def _update_note_size(self, note_id: int, width: float, height: float) -> None:
        if note_id in self._notes:
            self._notes[note_id].setRect(0, 0, width, height)
            self.notes_changed.emit()

    def _update_note_text(self, note_id: int, text: str) -> None:
        if note_id in self._notes:
            self._notes[note_id].set_text(text)
            self.notes_changed.emit()

    def _on_note_moved(self, note_id: int, old_x: float, old_y: float, new_x: float, new_y: float) -> None:
        action = MoveNoteAction(
            note_id=note_id,
            old_x=old_x,
            old_y=old_y,
            new_x=new_x,
            new_y=new_y,
            update_callback=self._update_note_position,
        )
        self._undo_manager.push(action)

    def _on_note_resized(self, note_id: int, old_w: float, old_h: float, new_w: float, new_h: float) -> None:
        action = ResizeNoteAction(
            note_id=note_id,
            old_width=old_w,
            old_height=old_h,
            new_width=new_w,
            new_height=new_h,
            update_callback=self._update_note_size,
        )
        self._undo_manager.push(action)

    def _on_note_text_changed(self, note_id: int, old_text: str, new_text: str) -> None:
        action = EditTextAction(
            note_id=note_id,
            old_text=old_text,
            new_text=new_text,
            update_callback=self._update_note_text,
        )
        self._undo_manager.push(action)

    def contextMenuEvent(self, event) -> None:
        scene_pos = self.mapToScene(event.pos())
        item = self._scene.itemAt(scene_pos, self.transform())

        menu = QMenu(self)

        if isinstance(item, NoteItem):
            bring_front_action = QAction("Bring to Front", self)
            bring_front_action.triggered.connect(lambda: self._bring_to_front(item))
            menu.addAction(bring_front_action)

            send_back_action = QAction("Send to Back", self)
            send_back_action.triggered.connect(lambda: self._send_to_back(item))
            menu.addAction(send_back_action)

            menu.addSeparator()

            color_menu = menu.addMenu("Change Color")
            for color in self._config.palette:
                r, g, b, a = color
                action = QAction(self)
                action.setText(f"  ")
                color_menu.addAction(action)

                def make_color_handler(c: tuple[int, int, int, int]) -> Callable:
                    return lambda: self._change_color(item, c)

                action.triggered.connect(make_color_handler(color))

                icon_color = QColor(r, g, b, a)
                action.setData(icon_color)

            menu.addSeparator()

            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self._delete_note(item))
            menu.addAction(delete_action)
        else:
            new_note_action = QAction("New Note", self)
            new_note_action.triggered.connect(self._create_note)
            menu.addAction(new_note_action)

        menu.exec(event.globalPos())

    def get_selected_note(self) -> NoteItem | None:
        selected = self._scene.selectedItems()
        if selected and isinstance(selected[0], NoteItem):
            return selected[0]
        return None

    def yank_selected(self) -> bool:
        item = self.get_selected_note()
        if not item:
            return False
        clipboard = QApplication.clipboard()
        clipboard.setText(item.text)
        return True

    def delete_selected(self) -> bool:
        item = self.get_selected_note()
        if not item:
            return False
        self._delete_note(item)
        return True

    def paste_as_new_note(self) -> bool:
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            return False

        color = random.choice(self._config.palette)
        order = self._get_max_order() + 1
        x, y = self._calculate_position_right()

        note = Note(
            id=self._next_id,
            x=x,
            y=y,
            width=self._config.default_width,
            height=self._config.default_height,
            text=text,
            order=order,
            color=color,
        )
        self._next_id += 1
        item = self._add_note_item(note, record_undo=True)
        self._scene.clearSelection()
        item.setSelected(True)
        self.notes_changed.emit()
        return True

    def select_next_note(self) -> None:
        if not self._notes:
            return

        sorted_ids = sorted(self._notes.keys())
        current = self.get_selected_note()

        if current is None:
            next_id = sorted_ids[0]
        else:
            current_idx = sorted_ids.index(current.note_id)
            next_idx = (current_idx + 1) % len(sorted_ids)
            next_id = sorted_ids[next_idx]

        self._scene.clearSelection()
        self._notes[next_id].setSelected(True)

    def select_prev_note(self) -> None:
        if not self._notes:
            return

        sorted_ids = sorted(self._notes.keys())
        current = self.get_selected_note()

        if current is None:
            prev_id = sorted_ids[-1]
        else:
            current_idx = sorted_ids.index(current.note_id)
            prev_idx = (current_idx - 1) % len(sorted_ids)
            prev_id = sorted_ids[prev_idx]

        self._scene.clearSelection()
        self._notes[prev_id].setSelected(True)

    def deselect_all(self) -> None:
        self._scene.clearSelection()

    def create_note_right_and_edit(self) -> None:
        x, y = self._calculate_position_right()
        item = self._create_note_at(x, y)
        self._scene.clearSelection()
        item.setSelected(True)
        item.enter_edit_mode()

    def create_note_below_and_edit(self) -> None:
        x, y = self._calculate_position_below()
        item = self._create_note_at(x, y)
        self._scene.clearSelection()
        item.setSelected(True)
        item.enter_edit_mode()

    def enter_edit_mode(self) -> bool:
        item = self.get_selected_note()
        if not item:
            return False
        item.enter_edit_mode()
        return True

    def exit_edit_mode(self) -> None:
        for item in self._notes.values():
            if item.is_editing():
                item.exit_edit_mode()

    def is_editing(self) -> bool:
        for item in self._notes.values():
            if item.is_editing():
                return True
        return False

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            if self.is_editing():
                self.exit_edit_mode()
            else:
                self._scene.clearSelection()
            event.accept()
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.is_editing():
            return

        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)

    def mousePressEvent(self, event) -> None:
        self.setFocus()

        if self.is_editing():
            scene_pos = self.mapToScene(event.pos())
            item = self._scene.itemAt(scene_pos, self.transform())
            editing_item = self.get_selected_note()
            if editing_item and editing_item.is_editing():
                if item != editing_item and item != editing_item._text_item:
                    self.exit_edit_mode()
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            item = self._scene.itemAt(scene_pos, self.transform())
            if not isinstance(item, NoteItem):
                self._panning = True
                self._pan_start = event.position()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._panning and self._pan_start is not None:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._panning:
            self._panning = False
            self._pan_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)
