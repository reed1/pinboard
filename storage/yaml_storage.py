from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from models.note import Note


@dataclass
class Config:
    palette: list[tuple[int, int, int, int]]
    text_color: tuple[int, int, int, int]
    canvas_background: tuple[int, int, int, int]
    font_family: str
    font_size: int
    default_width: int
    default_height: int
    padding: int


DEFAULT_CONFIG = {
    "palette": [
        (255, 230, 180, 255),  # Pastel yellow
        (180, 230, 180, 255),  # Pastel green
        (180, 210, 255, 255),  # Pastel blue
        (255, 200, 180, 255),  # Pastel peach
        (220, 190, 255, 255),  # Pastel purple
        (255, 200, 220, 255),  # Pastel pink
    ],
    "text_color": (40, 40, 40, 255),
    "canvas_background": (40, 40, 40, 255),
    "font_family": "Roboto",
    "font_size": 16,
    "default_width": 240,
    "default_height": 160,
    "padding": 20,
}


def load_notes(filepath: Path) -> list[Note]:
    if not filepath.exists():
        return []

    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    if not data:
        return []

    return [Note.from_dict(n) for n in data.get("notes", [])]


def save_notes(filepath: Path, notes: list[Note]) -> None:
    data = {"notes": [n.to_dict() for n in notes]}
    with open(filepath, "w") as f:
        yaml.dump(data, f, default_flow_style=None, sort_keys=False)


def load_config(user_config_path: Path | None = None) -> Config:
    data = dict(DEFAULT_CONFIG)

    if user_config_path and user_config_path.exists():
        with open(user_config_path, "r") as f:
            user_data = yaml.safe_load(f)
        if user_data:
            data.update(user_data)

    return Config(
        palette=[tuple(c) for c in data["palette"]],
        text_color=tuple(data["text_color"]),
        canvas_background=tuple(data["canvas_background"]),
        font_family=data["font_family"],
        font_size=data["font_size"],
        default_width=data["default_width"],
        default_height=data["default_height"],
        padding=data["padding"],
    )
