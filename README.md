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
| Paste as new note | `P` |
| Select next note | `Tab` / `J` / `L` |
| Select prev note | `Shift+Tab` / `K` / `H` |
| Scroll | `Ctrl+H/J/K/L` or arrow keys |
| Undo | `Ctrl+Z` or `U` |
| Redo | `Ctrl+Shift+Z` |
| Quit | `Q` |

## Configuration

Edit `config.yaml` to customize:

```yaml
palette:
  - [255, 255, 200, 255]  # Light yellow (RGBA)
  - [200, 255, 200, 255]  # Light green
  - [200, 230, 255, 255]  # Light blue
  - [255, 220, 200, 255]  # Light peach
  - [230, 200, 255, 255]  # Light purple
  - [255, 200, 220, 255]  # Light pink

font_family: Roboto
font_size: 12

default_width: 180
default_height: 120
padding: 20
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
next_id: 2
```

## Project Structure

```
pinboard/
├── main.py              # Entry point
├── config.yaml          # Application configuration
├── undo_manager.py      # Undo/redo stack
├── models/
│   └── note.py          # Note dataclass
├── storage/
│   └── yaml_storage.py  # YAML persistence
└── widgets/
    ├── canvas.py        # Main canvas
    └── note_item.py     # Note widget
```

## License

MIT
