from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from models.note import Note


class Action(ABC):
    @abstractmethod
    def undo(self) -> None:
        pass

    @abstractmethod
    def redo(self) -> None:
        pass


@dataclass
class CreateNoteAction(Action):
    note_id: int
    delete_callback: Callable[[int], None]
    recreate_callback: Callable[["Note"], None]
    note_data: "Note"

    def undo(self) -> None:
        self.delete_callback(self.note_id)

    def redo(self) -> None:
        self.recreate_callback(self.note_data)


@dataclass
class DeleteNoteAction(Action):
    note_data: "Note"
    recreate_callback: Callable[["Note"], None]
    delete_callback: Callable[[int], None]

    def undo(self) -> None:
        self.recreate_callback(self.note_data)

    def redo(self) -> None:
        self.delete_callback(self.note_data.id)


@dataclass
class MoveNoteAction(Action):
    note_id: int
    old_x: float
    old_y: float
    new_x: float
    new_y: float
    update_callback: Callable[[int, float, float], None]

    def undo(self) -> None:
        self.update_callback(self.note_id, self.old_x, self.old_y)

    def redo(self) -> None:
        self.update_callback(self.note_id, self.new_x, self.new_y)


@dataclass
class ResizeNoteAction(Action):
    note_id: int
    old_width: float
    old_height: float
    new_width: float
    new_height: float
    update_callback: Callable[[int, float, float], None]

    def undo(self) -> None:
        self.update_callback(self.note_id, self.old_width, self.old_height)

    def redo(self) -> None:
        self.update_callback(self.note_id, self.new_width, self.new_height)


@dataclass
class EditTextAction(Action):
    note_id: int
    old_text: str
    new_text: str
    update_callback: Callable[[int, str], None]

    def undo(self) -> None:
        self.update_callback(self.note_id, self.old_text)

    def redo(self) -> None:
        self.update_callback(self.note_id, self.new_text)


@dataclass
class ChangeColorAction(Action):
    note_id: int
    old_color: tuple[int, int, int, int]
    new_color: tuple[int, int, int, int]
    update_callback: Callable[[int, tuple[int, int, int, int]], None]

    def undo(self) -> None:
        self.update_callback(self.note_id, self.old_color)

    def redo(self) -> None:
        self.update_callback(self.note_id, self.new_color)


@dataclass
class ChangeOrderAction(Action):
    note_id: int
    old_order: int
    new_order: int
    update_callback: Callable[[int, int], None]

    def undo(self) -> None:
        self.update_callback(self.note_id, self.old_order)

    def redo(self) -> None:
        self.update_callback(self.note_id, self.new_order)


class UndoManager:
    def __init__(self, max_size: int = 100):
        self._undo_stack: list[Action] = []
        self._redo_stack: list[Action] = []
        self._max_size = max_size

    def push(self, action: Action) -> None:
        self._undo_stack.append(action)
        self._redo_stack.clear()
        if len(self._undo_stack) > self._max_size:
            self._undo_stack.pop(0)

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        action = self._undo_stack.pop()
        action.undo()
        self._redo_stack.append(action)
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        action = self._redo_stack.pop()
        action.redo()
        self._undo_stack.append(action)
        return True

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()
