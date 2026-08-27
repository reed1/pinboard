from __future__ import annotations

import argparse
from pathlib import Path

from pinboard.commands import add as cmd_add
from pinboard.commands import delete as cmd_delete
from pinboard.commands import edit as cmd_edit
from pinboard.commands import list as cmd_list
from pinboard.commands import open as cmd_open


def main() -> None:
    parser = argparse.ArgumentParser(prog="pinboard", description="Sticky notes application")
    subparsers = parser.add_subparsers(dest="command", required=True)

    open_parser = subparsers.add_parser("open", help="Open a pinboard file in the GUI")
    open_parser.add_argument("file", type=Path, help="Path to the YAML file")

    list_parser = subparsers.add_parser("list", help="List the notes, sorted by id")
    list_parser.add_argument("file", type=Path, help="Path to the YAML file")
    list_parser.add_argument("--json", action="store_true", help="Print the notes as JSON")

    add_parser = subparsers.add_parser("add", help="Add a new note via CLI")
    add_parser.add_argument("file", type=Path, help="Path to the YAML file")
    add_parser.add_argument("text", help="Text content for the new note")
    add_parser.add_argument(
        "--metadata", help="JSON object to hang on the new note's metadata mapping"
    )

    edit_parser = subparsers.add_parser("edit", help="Replace the text of a note")
    edit_parser.add_argument("file", type=Path, help="Path to the YAML file")
    edit_parser.add_argument("id", type=int, help="Id of the note to edit")
    edit_parser.add_argument("text", help="New text content for the note")

    delete_parser = subparsers.add_parser("delete", help="Delete a note")
    delete_parser.add_argument("file", type=Path, help="Path to the YAML file")
    delete_parser.add_argument("id", type=int, help="Id of the note to delete")

    args = parser.parse_args()

    if args.command == "open":
        cmd_open.run(args)
    elif args.command == "list":
        cmd_list.run(args)
    elif args.command == "add":
        cmd_add.run(args)
    elif args.command == "edit":
        cmd_edit.run(args)
    elif args.command == "delete":
        cmd_delete.run(args)
    else:
        raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
