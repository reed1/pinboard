from __future__ import annotations

import argparse

from pinboard.models.note import utc_now
from pinboard.storage.yaml_storage import load_notes, save_notes


def run(args: argparse.Namespace) -> None:
    notes = load_notes(args.file)

    note = next((n for n in notes if n.id == args.id), None)
    if note is None:
        raise SystemExit(f"No note with id {args.id}")

    note.text = args.text
    note.edited_at = utc_now()
    save_notes(args.file, notes)
    print(f"Edited note {note.id}")
