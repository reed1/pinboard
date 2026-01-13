from __future__ import annotations

import argparse
from pathlib import Path

from commands import open as cmd_open
from commands import push as cmd_push


def main() -> None:
    parser = argparse.ArgumentParser(prog="pinboard", description="Sticky notes application")
    subparsers = parser.add_subparsers(dest="command", required=True)

    open_parser = subparsers.add_parser("open", help="Open a pinboard file in the GUI")
    open_parser.add_argument("file", type=Path, help="Path to the YAML file")

    push_parser = subparsers.add_parser("push", help="Add a new note via CLI")
    push_parser.add_argument("file", type=Path, help="Path to the YAML file")
    push_parser.add_argument("text", help="Text content for the new note")

    args = parser.parse_args()

    if args.command == "open":
        cmd_open.run(args)
    elif args.command == "push":
        cmd_push.run(args)
    else:
        raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
