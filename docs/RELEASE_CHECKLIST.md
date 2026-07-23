Scriptolator 1.0.0 RC1 Acceptance Test

Professional AI Narration

This checklist verifies that Scriptolator Version 1.0.0 works correctly from source, as a packaged executable, and after installation.

Record any failures before proceeding to release.

Test Environment

Windows version:

Scriptolator build:

Test date:

Tester:

Python version:

PyInstaller version:

Inno Setup version:

1. Source Startup

Launch Scriptolator with run.bat.

Splash screen appears.

Main window opens without errors.

Scriptolator icon appears in the title bar.

No unexpected console errors are shown.

About dialog shows Version 1.0.0.

Help menu opens correctly.

F1 opens the Quick Start Guide.

Notes:

2. Packaged EXE Startup

Rebuild with Scriptolator.spec.

Launch dist\Scriptolator.exe.

No console window appears.

Splash screen appears.

Main window opens.

Taskbar icon is correct.

Title bar icon is correct.

About dialog shows Version 1.0.0.

Built-in Help documents open.

Settings persist after closing and reopening.

Notes:

3. Voice Loading and Selection

Voice list loads successfully.

Language filter works.

English language variants appear correctly.

Narration Voice list updates when language changes.

Selecting a voice updates the current voice.

Favourite button changes between ☆ and ★.

Adding a favourite works.

Removing a favourite works.

★ Favorites filter shows only favourite voices.

Notes:

4. Voice Preview

Preview works with no script selection.

Preview reads only selected text when text is selected.

Speed changes affect preview.

Pitch changes affect preview.

Volume changes affect preview.

Preview failure produces a clear error message.

Application remains responsive during preview.

Notes:

5. Voice Profiles

Create a new Voice Profile.

Profile is saved in %LOCALAPPDATA%\Scriptolator\Profiles.

Load the profile.

Loaded voice and sliders match the saved values.

Rename the profile.

Save changes to the renamed profile.

Delete the profile.

Deleted profile no longer appears after restart.

Notes:

6. Script Workflow

Type a new script.

Open an existing .txt script.

Open dialog starts in the last-used script folder.

Save the script.

Save dialog uses the last-used save folder.

Clear the editor.

Clear confirmation appears when enabled.

Undo and redo work.

Unsaved changes are handled correctly when closing.

Notes:

7. MP3 Generation

Choose a valid output folder.

Default output folder is %LOCALAPPDATA%\Scriptolator\Output.

Enter a valid output filename.

Click Generate MP3.

Generate button changes during generation.

Generation animation is visible.

Application remains responsive.

Generated MP3 is created.

Play MP3 opens the generated file.

Open Output Folder opens the correct folder.

Existing file overwrite warning works.

Locked/open MP3 produces a clear permission error.

Invalid filename handling works.

Notes:

8. Project Workflow

Create a new project.

Save Project uses %LOCALAPPDATA%\Scriptolator\Projects by default.

Save Project As works.

Open Project works.

Project restores script text.

Project restores voice selection.

Project restores Speed, Pitch and Volume.

Project restores output information.

Project appears in Recent Projects.

Recent Projects entry opens the correct project.

Clear Recent Projects works.

.scriptolator backup file is created after overwriting a project.

Legacy .scriptalator project loading still works.

Notes:

9. Recovery

Make an unsaved change.

Confirm recovery data is created in %LOCALAPPDATA%\Scriptolator\Recovery.

Simulate an unexpected shutdown.

Restart Scriptolator.

Recovery prompt appears.

Restore recovers the script and settings.

Discard removes recovery data.

No stale recovery prompt appears after a clean close.

Notes:

10. Settings and Persistence

Settings file exists at %LOCALAPPDATA%\Scriptolator\Settings\settings.ini.

Last voice is remembered.

Last language is remembered.

Speed is remembered.

Pitch is remembered.

Volume is remembered.

Favourite voices are remembered.

Last profile is remembered when enabled.

Output folder is remembered when enabled.

Window size and position are remembered when enabled.

Recent Projects persist.

Script open/save folders persist.

Notes:

11. Logging

Log file exists at %LOCALAPPDATA%\Scriptolator\Logs\scriptolator.log.

Startup is logged.

Application data path is logged.

Successful generation is logged.

Failed generation is logged.

Log file remains readable after restart.

Log rotation does not create errors.

Notes:

12. Documentation

Quick Start Guide opens.

User Guide opens.

Keyboard Shortcuts opens.

FAQ opens.

Troubleshooting opens.

Release Notes opens.

F1 opens Quick Start.

About dialog documentation buttons work.

Markdown formatting is readable.

Missing-document handling shows a clear warning.

Notes:

13. Installer

Build installer with build_installer.bat.

Installer file is created.

Installer icon is correct.

Installation completes without administrator rights.

Start Menu shortcut is created.

Optional Desktop shortcut works.

Scriptolator launches after installation.

Installed Help system works.

Installed Preview works.

Installed MP3 generation works.

Upgrade installation preserves settings and user files.

Uninstall removes application files and shortcuts.

Uninstall preserves Projects, Profiles and Output.

Reinstallation works.

Notes:

14. Clean-PC Test

Test on a Windows PC with no Python, VS Code, Git or virtual environment.

Installer launches.

Installation completes.

Scriptolator launches.

Voices load.

Preview works.

MP3 generation works.

Help documents open.

Settings persist.

Uninstall works.

No missing dependency errors appear.

Notes:

15. Release Decision

Blocking Issues

List any issue that must be fixed before release:







Non-Blocking Issues

List issues that may be deferred to Version 1.0.1:







Final Result

PASS — Ready for Version 1.0.0 release

FAIL — Additional work required

Approved by:

Date:

© 2026 Johan Dehlen

Scriptolator 1.0.0