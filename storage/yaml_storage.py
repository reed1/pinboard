from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from models.note import Note


@dataclass
class Config:
    palette: list[tuple[int, int, int, int]]
    default_width: int
    default_height: int
    padding: int


DEFAULT_PALETTE = [
    (255, 255, 200, 255),
    (200, 255, 200, 255),
    (200, 230, 255, 255),
    (255, 220, 200, 255),
    (230, 200, 255, 255),
    (255, 200, 220, 255),
]


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
        return Config(
            palette=DEFAULT_PALETTE,
            default_width=180,
            default_height=120,
            padding=20,
        )

    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    if not data:
        return Config(
            palette=DEFAULT_PALETTE,
            default_width=180,
            default_height=120,
            padding=20,
        )

    palette = [tuple(c) for c in data.get("palette", DEFAULT_PALETTE)]
    default_width = data.get("default_width", 180)
    default_height = data.get("default_height", 120)
    padding = data.get("padding", 20)

    return Config(
        palette=palette,
        default_width=default_width,
        default_height=default_height,
        padding=padding,
    )
