# Scriptolator

**Transform scripts into professional AI narration**

Scriptolator is a Windows desktop application for turning written scripts into high-quality MP3 narration using Microsoft Edge Neural Voices.

It is designed for content creators who want a fast, focused narration workflow without subscriptions or per-character generation fees.

## Current Version

**0.5.0**

Scriptolator is currently in active pre-release development.

## Features

### Narration

- High-quality Microsoft Edge Neural Voices
- English-first language selection
- Friendly language and voice names
- Voice filtering by language
- Favorite voices
- Script-based voice preview
- Adjustable speaking speed
- Adjustable pitch
- Adjustable volume
- Double-click slider reset
- Responsive background narration generation
- Automatic `.mp3` filename extension
- Output overwrite protection
- Play generated narration
- Open the output folder

### Narration Profiles

- Fully user-defined narration profiles
- Stores language, voice, speed, pitch, and volume
- Create, save, rename, and delete profiles
- Shows when a selected profile has unsaved changes
- Remembers the last selected profile
- Opens the profiles folder directly
- Profiles are stored as portable JSON files

### Projects

- Save and load `.scriptolator` project files
- Opens legacy `.scriptalator` projects
- Recent Projects menu
- Drag-and-drop `.txt` and `.md` scripts
- Remembers project narration and output settings
- Dynamic project name in the window title

### Productivity

- Live word count
- Estimated narration duration
- `Ctrl+Enter` to generate narration
- Standard File and Edit menu shortcuts
- Remembers the last output folder
- Remembers window size, position, and maximized state
- Help menu and About dialog
- Copyable system information for troubleshooting

## Requirements

- Windows
- Python 3.14 or later
- PySide6
- edge-tts
- mutagen

## Installation

Clone the repository:

```bat
git clone https://github.com/JohanDehlen/Scriptolator.git
cd Scriptolator
```

Create and activate a virtual environment:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

Install the dependencies:

```bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Compile-check the project:

```bat
build.bat
```

Start Scriptolator:

```bat
run.bat
```

## Project Structure

```text
Scriptolator/
├── src/
│   └── scriptalator/
├── output/
├── profiles/
├── projects/
├── build.bat
├── run.bat
└── requirements.txt
```

The internal Python package retains the historical `scriptalator` name for compatibility. The public application and repository name are **Scriptolator**.

## Project Files

New projects use:

```text
.scriptolator
```

Legacy `.scriptalator` projects remain supported and can be opened normally.

## Narration Profiles

Narration profiles are stored in the local `profiles` folder. They are normal JSON files and can be backed up or copied between Scriptolator installations.

A profile stores:

- Language
- Voice
- Speed
- Pitch
- Volume

Project-specific information such as script text, output folder, and output filename remains in the project file rather than the narration profile.

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+N` | New Project |
| `Ctrl+O` | Open Project |
| `Ctrl+S` | Save Project |
| `Ctrl+Enter` | Generate MP3 |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+X` | Cut |
| `Ctrl+C` | Copy |
| `Ctrl+V` | Paste |
| `Ctrl+A` | Select All |

## Development Status

The current development focus is stability, visual polish, documentation, and preparation for the first public release.