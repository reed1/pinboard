# Pinboard

A lightweight desktop sticky notes application with YAML-based storage for easy version control.

## Features

- **Sticky Notes** - Create, move, resize, and delete notes
- **Drag & Drop** - Move notes by dragging
- **Resize** - Drag corner handles to resize
- **Text Editing** - Double-click or press E to edit note text
- **Color Palette** - Right-click to change note colors (configurable pastel palette)
- **Z-Ordering** - Bring to front / send to back via right-click menu
- **Undo/Redo** - Ctrl+Z / Ctrl+Shift+Z
- **Auto-save** - Changes saved automatically (debounced 500ms)
- **Git-friendly** - Notes stored in plain YAML files

## Installation

```bash
uv sync
```

## Usage

```bash
uv run python main.py <path/to/notes.yaml>
```

The YAML file will be created if it doesn't exist.

Notes can also be worked on without the GUI, which is how other tools reach a board:

```bash
pinboard list <file> [--json]      # notes sorted by id
pinboard add <file> <text>         # add a note
pinboard edit <file> <id> <text>   # replace a note's text
pinboard delete <file> <id>        # remove a note
```

`edit` and `delete` exit non-zero when no note carries that id. An open GUI window picks these
changes up on its own — it watches the file.

## Keybindings

Look at `@src/pinboard/keybindings.py`. This can be extended on local `config.py`

## Configuration

Create `~/.config/pinboard/config.yaml` to override defaults (only specify what you want to change):

```yaml
font_family: Roboto
font_size: 20
palette:
  - [255, 230, 180, 255]  # Pastel yellow (RGBA)
  - [180, 230, 180, 255]  # Pastel green
```

Available options: `palette`, `text_color`, `canvas_background`, `font_family`, `font_size`, `default_width`, `default_height`, `padding`

For custom keybindings and scripting, create `~/.config/pinboard/config.py`:

```python
from pinboard import PinboardAPI

pb: PinboardAPI

pb.add_keybinding("Ctrl+Shift+N", lambda: pb.toast("Hello!"))
```

## Data Format

Notes are stored in YAML for easy diffing and version control:

```yaml
notes:
  - id: 1
    x: 20
    y: 20
    width: 180
    height: 120
    text: "My first note"
    order: 1
    color: [255, 255, 200, 255]
    created_at: "2024-01-15T10:30:00Z"
    edited_at: "2024-01-15T11:45:00Z"
    adjusted_at: "2024-01-15T12:00:00Z"
    metadata:
      ticket: ENG-441
```

Timestamps use ISO 8601 UTC format. `created_at` is set when a note is created. `edited_at` is updated when text content changes. `adjusted_at` is updated when position, size, z-order, or color changes.

`metadata` is a free-form mapping for other tools to hang their own keys off a note, kept out of
the text so it does not show on the board. Pinboard never reads what is in it — it carries the keys
through load and save untouched, so an open GUI window, an undo, or a `pinboard edit` will not drop
them. A note with no metadata has the key omitted rather than written as `{}`, so notes that never
carry any stay byte-identical to how they look today.

## Project Structure

```
pinboard/
└── src/pinboard/            # Package (importable as `pinboard`)
    ├── __init__.py          # Exports PinboardAPI, pb
    ├── cli.py               # Entry point
    ├── api.py               # Scripting API
    ├── window.py            # Main window
    ├── keybindings.py       # Default keybindings
    ├── undo_manager.py      # Undo/redo stack
    ├── models/
    │   └── note.py          # Note dataclass
    ├── storage/
    │   └── yaml_storage.py  # YAML persistence, embedded defaults
    ├── widgets/
    │   ├── canvas.py        # Main canvas
    │   ├── note_item.py     # Note widget
    │   └── toast.py         # Toast notifications
    └── commands/
        ├── open.py          # GUI open command
        ├── list.py          # CLI list command
        ├── add.py           # CLI add command
        ├── edit.py          # CLI edit command
        └── delete.py        # CLI delete command
```

## License

MIT
