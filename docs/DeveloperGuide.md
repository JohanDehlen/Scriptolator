# Scriptolator

**Professional AI Narration**

# Developer Guide

**Version 1.0.0**

---

# Purpose

This guide is intended for developers maintaining or extending Scriptolator.

It describes the project structure, architecture, build process and release workflow.

---

# Repository Layout

```
Scriptolator/
│
├── src/
├── docs/
├── assets/
├── installer/
├── tests/
├── build.bat
├── run.bat
└── Scriptolator.spec
```

---

# Source Structure

```
src/scriptolator/
│
├── main.py
├── main_window.py
├── services/
├── widgets/
├── resources/
└── version.py
```

- **main.py** – application entry point.
- **main_window.py** – main application window.
- **services/** – business logic and persistence.
- **widgets/** – reusable UI components.
- **resources/** – icons, splash screen and bundled assets.

---

# Architecture

Scriptolator separates presentation from application services.

## Widgets

Widgets present information and collect user input.

## Services

Services encapsulate application logic such as:

- Narration generation
- Projects
- Settings
- Profiles
- Recovery
- Logging

Widgets should call services rather than implement business logic directly.

---

# Data Storage

Version 1.0 stores user data outside the application source when packaged.

Typical folders include:

- output/
- profiles/
- projects/
- recovery/
- logs/

Settings persist between sessions.

---

# Building

Development:

```
build.bat
run.bat
```

Executable:

```
python -m PyInstaller --clean --noconfirm Scriptolator.spec
```

Output:

```
dist/Scriptolator.exe
```

---

# Release Process

1. Update `version.py`.
2. Update CHANGELOG.md.
3. Run acceptance tests.
4. Build the executable.
5. Test on a clean Windows PC.
6. Create the GitHub release.
7. Tag the release.
8. Publish documentation.

---

# Coding Standards

- Prefer descriptive names.
- Keep UI logic out of services.
- Keep services independent of widgets where practical.
- Use type hints.
- Add docstrings to public classes and methods.
- Preserve backward compatibility for project files where possible.

---

# Future Development

Every new feature should satisfy at least one of these goals:

- Improve reliability.
- Improve usability.
- Improve narration quality.
- Improve workflow efficiency.

Avoid feature creep that moves Scriptolator away from its core purpose: creating professional AI narration.

---

© 2026 Johan Dehlen

Scriptolator 1.0.0
