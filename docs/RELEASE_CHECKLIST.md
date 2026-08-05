Scriptolator 1.1.0 Release Acceptance Test
==========================================

Purpose
-------

This checklist verifies that Scriptolator Version 1.1.0 works correctly from source, as a packaged executable, and as an in-place upgrade over Version 1.0.0.

Release candidate
-----------------

Version: 1.1.0
Branch: main
Installer: installer\output\ScriptolatorSetup-1.1.0.exe

1. Repository hygiene
---------------------

[ ] `git status` is clean.
[ ] No `.env` file is tracked.
[ ] No `*.before-*` backup file is tracked.
[ ] No temporary `apply_*.py`, `diagnose_*.py` or release patch script is tracked.
[ ] `requirements.txt` includes Azure Speech and keyring.
[ ] Version is 1.1.0 in `version.py`, `build_installer.bat` and `Scriptolator.iss`.

2. Source launch
----------------

[ ] Scriptolator starts from `src\scriptalator\main.py`.
[ ] Splash screen closes normally.
[ ] Main window appears and remains responsive.
[ ] About dialog shows Version 1.1.0.
[ ] About dialog describes both Microsoft Edge and Microsoft Azure AI Speech.

3. Microsoft Edge
-----------------

[ ] Edge can be selected.
[ ] Edge voice catalogue loads in the background.
[ ] Language filtering works.
[ ] Voice labels are concise.
[ ] Preview works.
[ ] Full MP3 generation works.
[ ] Generated MP3 plays correctly.

4. Microsoft Azure AI Speech
----------------------------

[ ] Azure Settings dialog opens.
[ ] Key field is masked.
[ ] Correct key and region pass Test Connection.
[ ] Azure voices load after Azure is selected.
[ ] Jorge Multilingual is available.
[ ] Jorge Multilingual preview works.
[ ] Full Jorge Multilingual narration works.
[ ] Azure key is stored in Windows Credential Manager.
[ ] Azure key is not written to `settings.ini`, projects or profiles.
[ ] Clearing Azure settings removes the credential and returns the saved engine to Edge.

5. Narration Profiles
---------------------

[ ] Edge profile can be created.
[ ] Azure profile can be created.
[ ] Profiles store engine, language, voice, speed, pitch and volume.
[ ] Loading an Azure profile switches to Azure.
[ ] Loading an Azure profile waits for voices and restores its voice.
[ ] Loading an Edge profile switches to Edge.
[ ] A Version 1.0 profile still loads and defaults to Edge.
[ ] Profile can be renamed.
[ ] Profile can be deleted after confirmation.

6. Projects and recovery
------------------------

[ ] New project can be created.
[ ] Project can be saved.
[ ] Project can be reopened.
[ ] Recent Projects works.
[ ] Script import works.
[ ] Script export works.
[ ] Recovery data is written.
[ ] Recovery is offered after an abnormal termination.
[ ] Recovery dialog does not block startup behind the splash screen.

7. Documentation
----------------

[ ] Quick Start Guide shows Version 1.1.0.
[ ] User Guide shows Version 1.1.0.
[ ] FAQ shows Version 1.1.0.
[ ] Keyboard Shortcuts shows Version 1.1.0.
[ ] Troubleshooting shows Version 1.1.0.
[ ] Release Notes begin with Version 1.1.0.
[ ] Documentation explains that Azure is optional.
[ ] Documentation states that each user supplies their own Azure key.
[ ] Documentation states that the developer's key is not distributed.

8. Packaged executable
----------------------

[ ] PyInstaller build completes successfully.
[ ] `dist\Scriptolator.exe` starts.
[ ] Splash screen closes.
[ ] Edge voices work in the packaged executable.
[ ] Azure Settings can read a locally saved credential.
[ ] Azure voices work in the packaged executable.
[ ] Azure preview works.
[ ] Azure generation works.
[ ] Help documents open from the packaged executable.
[ ] No console window appears during normal use.

9. Installer
------------

[ ] `build_installer.bat` completes successfully.
[ ] `ScriptolatorSetup-1.1.0.exe` is created.
[ ] Installer branding shows Version 1.1.0.
[ ] Installer describes both Edge and Azure.
[ ] Fresh installation succeeds.
[ ] Start Menu shortcut works.
[ ] Optional desktop shortcut works.
[ ] Uninstaller is registered.

10. Upgrade from Version 1.0.0
-----------------------------

[ ] Version 1.0.0 is installed first.
[ ] Version 1.1.0 installer runs without uninstalling Version 1.0.0.
[ ] Existing installation folder is reused.
[ ] Version 1.1.0 launches after upgrade.
[ ] Existing projects remain available.
[ ] Existing profiles remain available.
[ ] Existing settings remain available.
[ ] Azure can be configured after upgrade.

11. Clean-machine credential test
---------------------------------

[ ] Install Version 1.1.0 on a PC or Windows VM that has never stored the developer's Azure credential.
[ ] Open Azure Settings.
[ ] Subscription-key field is empty.
[ ] Azure cannot connect until a key is entered.
[ ] The installer contains no `.env` file.
[ ] The installer contains no Azure subscription key.
[ ] Microsoft Edge works without Azure configuration.

12. Final approval
------------------

[ ] All critical tests pass.
[ ] No known startup blocker remains.
[ ] No user credential is distributed.
[ ] Git tag `v1.1.0` points to the approved release commit.
[ ] Release installer checksum is recorded.

Final result
------------

[ ] PASS — Ready for Version 1.1.0 release
[ ] FAIL — Release blocked

Tester:
Date:
Commit:
Installer SHA-256:
Notes:
