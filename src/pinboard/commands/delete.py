from __future__ import annotations

import argparse

from pinboard.storage.yaml_storage import load_notes, save_notes


def run(args: argparse.Namespace) -> None:
    notes = load_notes(args.file)

    remaining = [n for n in notes if n.id != args.id]
    if len(remaining) == len(notes):
        raise SystemExit(f"No note with id {args.id}")

    save_notes(args.file, remaining)
    print(f"Deleted note {args.id}")
