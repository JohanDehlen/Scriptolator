# Scriptolator

**Transform scripts into professional AI narration**

Scriptolator is a Windows desktop application for turning written scripts into high-quality MP3 narration using Microsoft Edge and Microsoft Azure AI Speech voices.

It is designed for content creators who want a fast, focused workflow from written script to finished narration.

## Current Version

**1.1.0**

## Features

### Speech Engines

- Microsoft Edge voices
- Microsoft Azure AI Speech voices
- Fast switching between speech engines
- Background voice catalogue loading
- Secure Azure credential storage through Windows Credential Manager
- Azure connection testing
- Safe fallback to Microsoft Edge when Azure is not configured

Microsoft Edge can be used without an Azure account. Microsoft Azure AI Speech is optional and requires each user to provide their own Azure Speech subscription key and region.

### Narration

- Friendly language and voice names
- Voice filtering by language
- Favourite voices
- Script-based voice previews
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
- Stores speech engine, language, voice, speed, pitch and volume
- Create, save, rename and delete profiles
- Automatically restores the saved speech engine and voice
- Existing Version 1.0 profiles remain compatible and default to Microsoft Edge
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
- Automatic recovery after an unexpected shutdown

### Productivity

- Live word count
- Estimated narration duration
- Keyboard shortcuts
- Standard File and Edit menu shortcuts
- Remembers the last output folder
- Remembers window size, position and maximized state
- Help menu and About dialog
- Copyable system information for troubleshooting
- Built-in Quick Start Guide, User Guide, FAQ, Troubleshooting Guide and Release Notes

## Requirements

### Installed application

- Microsoft Windows 10 or Windows 11
- Active Internet connection for voice discovery, previews and narration generation
- An Azure Speech resource only when using Microsoft Azure AI Speech

### Source development

- Python 3.14 or later
- PySide6
- edge-tts
- mutagen
- azure-cognitiveservices-speech
- keyring

## Installation from Source

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
├── docs/
├── installer/
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

## Azure Privacy and Security

Scriptolator does not include the developer's Azure key.

Each user who chooses Microsoft Azure AI Speech must enter their own Azure Speech subscription key and region. The key is stored on that user's PC in Windows Credential Manager and is not written to projects, profiles, `settings.ini`, the installer or the GitHub repository.

Users who do not have Azure can continue using Microsoft Edge.

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

Version 1.1.0 introduces multi-engine narration with Microsoft Edge and Microsoft Azure AI Speech.
