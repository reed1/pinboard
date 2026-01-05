from dataclasses import dataclass, field


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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "text": self.text,
            "order": self.order,
            "color": list(self.color),
        }

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
        )
