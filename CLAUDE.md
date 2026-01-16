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

## Controls

| Action | Input |
|--------|-------|
| Pan canvas | Drag empty space |
| Zoom | Mouse wheel |
| Reset viewport | `Backspace` |
| Create note (right) | Right-click empty space → "New Note", or `I` |
| Create note (below) | `O` |
| Move note | Drag note |
| Resize note | Click to select, drag corners |
| Edit text | Double-click, or `E` |
| Delete note | Right-click → "Delete", or `X` / `Del` |
| Bring to front | Right-click → "Bring to Front" |
| Send to back | Right-click → "Send to Back" |
| Change color | Right-click → "Change Color" |
| Yank (copy) text | `Y` |
| Paste as new note | `P` / `Ctrl+V` |
| Select next note | `Tab` / `J` / `L` |
| Select prev note | `Shift+Tab` / `K` / `H` |
| Scroll | `Ctrl+H/J/K/L` or arrow keys |
| Undo | `Ctrl+Z` or `U` |
| Redo | `Ctrl+Shift+Z` |
| Quit | `Q` |

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
next_id: 2
```

Timestamps use ISO 8601 UTC format. `created_at` is set when a note is created. `edited_at` is updated when text content changes. `adjusted_at` is updated when position, size, z-order, or color changes.

## Project Structure

```
pinboard/
├── main.py                  # Entry point
└── src/pinboard/            # Package (importable as `pinboard`)
    ├── __init__.py          # Exports PinboardAPI, pb
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
        └── push.py          # CLI push command
```

## License

MIT
