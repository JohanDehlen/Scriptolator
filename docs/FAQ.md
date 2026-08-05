# Scriptolator Frequently Asked Questions (FAQ)

**Professional AI Narration**

**Version 1.1.0**

---

# General

## What is Scriptolator?

Scriptolator is a Windows desktop application that converts written scripts into professional AI narration using Microsoft Edge or Microsoft Azure AI Speech voices.

---

## Which speech engine should I choose?

Choose **Microsoft Edge** when you want free Microsoft voices without configuring an Azure account.

Choose **Microsoft Azure AI Speech** when you want Azure voices, including multilingual voices such as Jorge Multilingual.

Azure is optional.

---

## Do I need an Internet connection?

Yes.

Both Microsoft Edge and Microsoft Azure AI Speech are cloud-based. An active Internet connection is required for voice discovery, previews and narration generation.

---

## Do I need an Azure account?

No, not when using Microsoft Edge.

To use Microsoft Azure AI Speech, you need an Azure Speech resource, a subscription key and the resource region.

---

## Is the developer's Azure key included with Scriptolator?

No.

Scriptolator does not include the developer's Azure key. Every user who selects Azure must enter their own key and region.

The key is stored securely in Windows Credential Manager on that user's PC. It is not stored in projects, profiles, `settings.ini`, the installer or GitHub.

---

## Which operating systems are supported?

Scriptolator Version 1.1.0 is designed for Microsoft Windows 10 and Windows 11.

---

# Scripts and Projects

## What is the difference between a Script and a Project?

A **Script** contains only narration text.

A **Project** stores the script together with narration settings, the selected voice, profile and related project information so you can continue working later.

---

## Where are Projects stored?

Projects are stored in the folder you choose when saving them.

---

## Where are generated MP3 files stored?

MP3 files are written to the output location you select.

The preferred output folder can be changed from within Scriptolator.

---

# Speech Engines and Voices

## How do I configure Azure?

1. Open Scriptolator.
2. Click **Configure Azure...** or open **Tools → Microsoft Azure AI Speech...**.
3. Enter the subscription key for your Azure Speech resource.
4. Enter the Azure region, such as `southafricanorth`.
5. Click **Test Connection**.
6. Click **Save** after the test succeeds.

---

## Can I save favourite voices?

Yes.

Click the ☆ button beside the voice list to add a voice to your favourites.

Use the **★ Favorites** language filter to display only favourite voices.

---

## What are Narration Profiles?

Narration Profiles save combinations of:

- Speech engine
- Language
- Voice
- Speed
- Pitch
- Volume

Loading a profile restores its saved engine and voice. Profiles created in Version 1.0 remain compatible and use Microsoft Edge by default.

---

## Can I delete a profile?

Yes.

Select the profile and click **Delete**. Scriptolator asks for confirmation before deleting it.

---

# Updates

## Can Version 1.1 be installed over Version 1.0?

Yes.

Close Scriptolator and run the Version 1.1 installer. It uses the same installation identity and updates the existing installation.

Projects, profiles, settings and Azure credentials are stored outside the application installation folder and should remain available.

---

## Does Scriptolator update itself automatically?

Not currently.

To update, download and run the newer Scriptolator installer. You do not normally need to uninstall the previous version first.

---

# Recovery

## What happens if Scriptolator closes unexpectedly?

Scriptolator automatically stores recovery information while you work.

If the application closes unexpectedly, it offers to restore the recoverable work when Scriptolator starts again.

---

# Troubleshooting

## Preview does not produce any sound.

Check:

- Speakers or headphones
- Windows volume
- The selected playback device
- Internet connectivity
- That a valid voice is selected
- Azure key and region when using Azure

---

## Narration generation failed.

Verify:

- Internet connectivity
- The selected output folder is writable
- The destination file is not open in another application
- The correct speech engine is selected
- Azure is configured correctly when using Azure

Review the application log if the problem continues.

---

## Where are log files stored?

Scriptolator writes diagnostic logs automatically. Their location is shown in the application information and troubleshooting tools.

---

# Getting More Help

Additional documentation is available from the Help menu:

- Quick Start Guide
- User Guide
- Keyboard Shortcuts
- Troubleshooting Guide
- Release Notes

---

© 2026 Johan Dehlen

Scriptolator 1.1.0
