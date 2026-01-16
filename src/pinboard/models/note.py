from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Note:
    id: int
    x: float
    y: float
    width: float
    height: float
    text: str
    order: int
    color: tuple[int, int, int, int] = field(default_factory=lambda: (255, 255, 200, 255))
    created_at: str | None = None
    edited_at: str | None = None
    adjusted_at: str | None = None

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "text": self.text,
            "order": self.order,
            "color": list(self.color),
        }
        if self.created_at:
            d["created_at"] = self.created_at
        if self.edited_at:
            d["edited_at"] = self.edited_at
        if self.adjusted_at:
            d["adjusted_at"] = self.adjusted_at
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(
            id=data["id"],
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            text=data["text"],
            order=data["order"],
            color=tuple(data["color"]),
            created_at=data.get("created_at"),
            edited_at=data.get("edited_at"),
            adjusted_at=data.get("adjusted_at"),
        )
