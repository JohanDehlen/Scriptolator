# Scriptolator Release Notes

**Professional AI Narration**

## Version 1.1.0

**Microsoft Azure AI Speech and Multi-Engine Narration**

---

# Overview

Version 1.1.0 expands Scriptolator from an Edge-only narration application into a multi-engine speech production tool.

You can now choose between Microsoft Edge voices and Microsoft Azure AI Speech voices for previews and full MP3 narration generation.

---

# New in Version 1.1.0

## Microsoft Azure AI Speech

- Added Microsoft Azure AI Speech as a second narration engine.
- Added support for Azure multilingual voices, including Jorge Multilingual.
- Added Azure voice discovery and background catalogue loading.
- Added Azure-powered voice previews.
- Added full Azure MP3 narration generation.
- Added an Azure connection test that verifies credentials and reports the number of available voices.

Azure AI Speech requires an Azure Speech resource, subscription key and region.

---

## Speech Engine Selection

- Added a Speech Engine selector to the Voice Panel.
- Switch between Microsoft Edge and Microsoft Azure AI Speech.
- The selected engine is remembered between sessions.
- Scriptolator falls back safely to Microsoft Edge when Azure is not configured.
- Engine switching reloads the correct voice catalogue without freezing the interface.

---

## Secure Azure Configuration

- Added a dedicated Microsoft Azure AI Speech settings dialog.
- Azure subscription keys are masked in the interface.
- Subscription keys are stored securely in Windows Credential Manager.
- Azure keys are not written to projects, profiles, `settings.ini` or GitHub.
- Added options to test, save and clear Azure settings.

---

## Engine-Aware Profiles

Narration Profiles now remember:

- Speech engine
- Language
- Voice
- Speed
- Pitch
- Volume

Loading an Azure profile automatically switches to Azure, loads the Azure voice catalogue and restores the saved voice.

Profiles created before Version 1.1.0 remain compatible and default to Microsoft Edge.

---

## Cleaner Voice Selection

- Shortened long Microsoft Edge voice descriptions.
- Removed redundant Microsoft branding and repeated language text from Edge voice labels.
- Voice labels now focus on the speaker name and gender.
- Azure multilingual names remain descriptive, such as `Jorge Multilingual — Male`.
- Internal Microsoft voice identifiers remain unchanged.

---

## Reliability and Performance

- Voice catalogues now load in background threads.
- Switching engines no longer blocks the interface.
- Improved splash-screen and startup reliability.
- Startup recovery is deferred until the main window is visible.
- Narration generation records the selected engine in the application log.
- Engine controls are disabled while narration generation is running.
- Improved validation and error messages for multi-engine narration.

---

## Installer and Packaging

- Updated Scriptolator to Version 1.1.0.
- Added Azure Speech SDK support to the packaged executable.
- Added Windows Credential Manager support to the packaged executable.
- Updated the installer description for Edge and Azure narration.
- Version 1.1.0 can be installed over Version 1.0.0 without uninstalling first.
- Existing profiles, projects, settings and Azure credentials remain stored outside the application installation folder.

---

## Documentation

Updated documentation now covers:

- Microsoft Edge narration
- Microsoft Azure AI Speech narration
- Azure setup and secure key storage
- Speech engine selection
- Engine-aware profiles
- Version 1.1.0 workflows

---

# Version 1.0.0

**Initial Public Release**

Version 1.0.0 introduced the original Scriptolator workflow:

- Script creation and import
- Microsoft Edge Neural voices
- Voice previews
- MP3 narration generation
- Language filtering
- Favourite voices
- Narration Profiles
- Speed, Pitch and Volume controls
- Project saving and loading
- Recent Projects
- Automatic recovery
- Application logging
- Splash screen
- Keyboard shortcuts
- Built-in documentation
- Branded Windows installer

---

Thank you for using Scriptolator.

© 2026 Johan Dehlen

Scriptolator 1.1.0
