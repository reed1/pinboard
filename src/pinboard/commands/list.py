from __future__ import annotations

import argparse
import json

from pinboard.storage.yaml_storage import load_notes


def run(args: argparse.Namespace) -> None:
    notes = sorted(load_notes(args.file), key=lambda n: n.id)

    if args.json:
        print(json.dumps([n.to_dict() for n in notes]))
        return

    for note in notes:
        print(f"{note.id}\t{note.text.replace(chr(10), ' ')}")
