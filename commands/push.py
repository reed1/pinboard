from __future__ import annotations

import argparse
import random
from pathlib import Path

from models.note import Note, utc_now
from storage.yaml_storage import load_config, load_notes, save_notes


def run(args: argparse.Namespace) -> None:
    user_config_path = Path.home() / ".config" / "pinboard" / "config.yaml"
    config = load_config(user_config_path)

    notes = load_notes(args.file)

    if notes:
        max_id = max(n.id for n in notes)
        max_order = max(n.order for n in notes)
        last_note = max(notes, key=lambda n: n.id)
        x = last_note.x + last_note.width + config.padding
        y = last_note.y
    else:
        max_id = 0
        max_order = 0
        x = config.padding
        y = config.padding

    note = Note(
        id=max_id + 1,
        x=x,
        y=y,
        width=config.default_width,
        height=config.default_height,
        text=args.text,
        order=max_order + 1,
        color=random.choice(config.palette),
        created_at=utc_now(),
    )
    notes.append(note)
    save_notes(args.file, notes)
    print(f"Added note {note.id} at ({x}, {y})")
