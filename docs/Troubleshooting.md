# Scriptolator Troubleshooting Guide

**Professional AI Narration**

**Version 1.1.0**

---

# Introduction

This guide provides solutions to common Scriptolator problems.

Before contacting support, work through the relevant section below.

---

# Scriptolator Stops on the Splash Screen

## Try this first

Close stuck Python processes from Command Prompt:

```bat
taskkill /F /IM python.exe /T
```

Then launch Scriptolator again.

For an installed build, also check Task Manager for `Scriptolator.exe`.

## Additional checks

- Restart Windows if a hidden process remains.
- Review the latest Scriptolator log.
- Confirm the application files are complete.
- Reinstall Scriptolator if required.

---

# Voices Do Not Load

## Symptoms

- The voice list is empty.
- `Unable to load voices` is displayed.
- The selected engine remains in a loading state.

## Possible causes

- No Internet connection
- Temporary Microsoft service issue
- Firewall or security software blocking Scriptolator
- Invalid Azure key or region
- Azure not configured

## Solutions

1. Confirm the Internet connection works.
2. Check which Speech Engine is selected.
3. Switch to Microsoft Edge to determine whether the issue is Azure-specific.
4. When using Azure, open Azure Settings and click **Test Connection**.
5. Confirm the Azure region matches the Speech resource.
6. Restart Scriptolator.
7. Try again after a few minutes.

---

# Azure Cannot Be Selected

Azure requires a saved subscription key and region.

Open **Tools → Microsoft Azure AI Speech...**, enter the key and region, test the connection and save the settings.

Scriptolator falls back to Microsoft Edge when Azure is unavailable or has been cleared.

---

# Azure Connection Test Failed

Check:

- The subscription key was copied completely
- The region is correct, for example `southafricanorth`
- The key belongs to the same Azure Speech resource as the region
- The Azure Speech resource is active
- The Internet connection is working
- Firewall software is not blocking Scriptolator

Do not paste Azure keys into support messages or log reports.

---

# Preview Produces No Sound

Check:

- Windows is not muted
- Speakers or headphones are connected
- The correct playback device is selected
- A valid narration voice is selected
- Internet connectivity is available
- Azure configuration is valid when using Azure
- Windows can open MP3 files with a default audio player

---

# MP3 Generation Failed

## Possible causes

- Network interruption
- Invalid output location
- Destination file already open
- Temporary voice-service problem
- Invalid Azure credentials
- Azure quota or resource issue

## Solutions

- Retry generation
- Save to another folder
- Close applications using the destination MP3
- Test Azure again when using Azure
- Switch to Microsoft Edge to determine whether the issue is Azure-specific
- Review the application log

---

# A Profile Does Not Restore Its Voice

A Version 1.1 profile stores its Speech Engine and voice.

Check:

- The profile's saved engine is available
- Azure is configured when the profile uses Azure
- The saved voice is still returned by Microsoft
- The Internet connection is working

Profiles created before Version 1.1 default to Microsoft Edge.

---

# Azure Settings Are Missing on Another PC

This is expected.

Azure keys are stored in Windows Credential Manager on the computer where they were entered. They are not included in the installer and are not copied with profiles or projects.

Configure Azure separately on each PC.

---

# Output Folder Cannot Be Opened

Verify that:

- The folder still exists
- You have permission to access it
- The drive is connected when using removable or network storage

Choose a new output folder if necessary.

---

# Recovery Was Not Offered

Recovery information is available only when Scriptolator previously saved recoverable work.

Check that:

- Recovery was not already restored or discarded
- The recovery folder is accessible
- The application log does not show a recovery error

---

# Settings Were Not Remembered

Ensure Scriptolator can write to its application-data folder.

Avoid running the application from read-only media.

Azure keys are stored separately in Windows Credential Manager.

---

# Application Will Not Start

Try:

1. Run `taskkill /F /IM python.exe /T` when testing from source.
2. Restart Windows.
3. Launch Scriptolator again.
4. Review the latest log.
5. Reinstall Scriptolator if required.

---

# Log Files

Logs contain diagnostic information that can assist with troubleshooting.

When reporting a problem, include the relevant log but never include an Azure subscription key.

---

# Still Need Help?

Consult:

- Quick Start Guide
- User Guide
- FAQ
- Release Notes

Include:

- Scriptolator version
- Selected Speech Engine
- Windows version
- Steps to reproduce the problem
- Relevant log files

---

© 2026 Johan Dehlen

Scriptolator 1.1.0
