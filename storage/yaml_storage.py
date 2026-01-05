from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from models.note import Note


@dataclass
class Config:
    palette: list[tuple[int, int, int, int]]
    canvas_background: tuple[int, int, int, int]
    default_width: int
    default_height: int
    padding: int


def load_notes(filepath: Path) -> tuple[list[Note], int]:
    if not filepath.exists():
        return [], 1

    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    if not data:
        return [], 1

    notes = [Note.from_dict(n) for n in data.get("notes", [])]
    next_id = data.get("next_id", 1)
    return notes, next_id


def save_notes(filepath: Path, notes: list[Note], next_id: int) -> None:
    data = {
        "notes": [n.to_dict() for n in notes],
        "next_id": next_id,
    }
    with open(filepath, "w") as f:
        yaml.dump(data, f, default_flow_style=None, sort_keys=False)


def load_config(filepath: Path) -> Config:
    if not filepath.exists():
        raise FileNotFoundError(f"Config file not found: {filepath}")

    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    if not data:
        raise ValueError(f"Config file is empty: {filepath}")

    if "palette" not in data:
        raise ValueError("Config must contain 'palette'")
    if "canvas_background" not in data:
        raise ValueError("Config must contain 'canvas_background'")

    palette = [tuple(c) for c in data["palette"]]
    canvas_background = tuple(data["canvas_background"])
    default_width = data.get("default_width", 180)
    default_height = data.get("default_height", 120)
    padding = data.get("padding", 20)

    return Config(
        palette=palette,
        canvas_background=canvas_background,
        default_width=default_width,
        default_height=default_height,
        padding=padding,
    )
