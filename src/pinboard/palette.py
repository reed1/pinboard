from __future__ import annotations

import html
import subprocess

from pinboard.keybindings import Command

PROMPT = "Pinboard"


def _row(command: Command) -> str:
    key = html.escape(command.keys)
    return (
        f'<span alpha="60%"><b>{key}</b></span>'
        f'<span alpha="40%"> - </span>'
        f"{html.escape(command.description)}"
    )


def choose_command(commands: list[Command]) -> Command | None:
    rofi = subprocess.run(
        ["rofi", "-dmenu", "-i", "-no-custom", "-markup-rows", "-p", PROMPT, "-format", "i"],
        input="\n".join(_row(c) for c in commands),
        capture_output=True,
        text=True,
        check=False,
    )
    if rofi.returncode != 0:
        return None
    return commands[int(rofi.stdout.strip())]
