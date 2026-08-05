#define MyAppName "Scriptolator"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Johan Dehlen"
#define MyAppURL "https://scriptolator.com"
#define MyAppExeName "Scriptolator.exe"
#define MyAppDescription "Professional AI Narration"

[Setup]
AppId={{D4E0B94A-7D25-4C5F-AEAB-80C915D9C701}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppComments={#MyAppDescription}
AppContact={#MyAppURL}

DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableWelcomePage=no
UsePreviousAppDir=yes

PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

OutputDir=output
OutputBaseFilename=ScriptolatorSetup-{#MyAppVersion}

SetupIconFile=..\src\scriptalator\resources\scriptolator.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

WizardStyle=modern
WizardImageFile=branding\wizard.png
WizardSmallImageFile=branding\wizard_small.png
WizardImageStretch=yes
WizardImageBackColor=$230804
WizardSmallImageBackColor=$40100A

Compression=lzma2/ultra64
SolidCompression=yes

CloseApplications=yes
RestartApplications=no
CloseApplicationsFilter={#MyAppExeName}
AppMutex=JohanDehlen.Scriptolator

VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoCopyright=Copyright (C) 2026 Johan Dehlen

MinVersion=10.0.0
ShowLanguageDialog=no
SetupLogging=yes

Uninstallable=yes
CreateUninstallRegKey=yes
UpdateUninstallLogAppName=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
WelcomeLabel1=Welcome to the%nScriptolator Setup Wizard
WelcomeLabel2=This will install Scriptolator {#MyAppVersion} on your computer.%n%nScriptolator transforms written scripts into professional AI narration using Microsoft Edge and Microsoft Azure AI Speech voices.%n%nClose other applications before continuing, then click Next.
FinishedHeadingLabel=Scriptolator is ready
FinishedLabel=Scriptolator has been installed successfully.%n%nLaunch the application now or open the Quick Start Guide to create your first narration.
ClickFinish=Click Finish to complete Setup.
BeveledLabel=Scriptolator {#MyAppVersion}  •  Professional AI Narration

[Tasks]
Name: "desktopicon"; \
    Description: "Create a &desktop shortcut"; \
    GroupDescription: "Additional shortcuts:"; \
    Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; \
    DestDir: "{app}"; \
    Flags: ignoreversion

Source: "..\docs\QuickStart.md"; \
    DestDir: "{app}\docs"; \
    Flags: ignoreversion

Source: "..\docs\UserGuide.md"; \
    DestDir: "{app}\docs"; \
    Flags: ignoreversion

Source: "..\docs\KeyboardShortcuts.md"; \
    DestDir: "{app}\docs"; \
    Flags: ignoreversion

Source: "..\docs\FAQ.md"; \
    DestDir: "{app}\docs"; \
    Flags: ignoreversion

Source: "..\docs\Troubleshooting.md"; \
    DestDir: "{app}\docs"; \
    Flags: ignoreversion

Source: "..\docs\ReleaseNotes.md"; \
    DestDir: "{app}\docs"; \
    Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"; \
    Comment: "{#MyAppDescription}"

Name: "{group}\Quick Start Guide"; \
    Filename: "{app}\docs\QuickStart.md"; \
    WorkingDir: "{app}\docs"

Name: "{group}\User Guide"; \
    Filename: "{app}\docs\UserGuide.md"; \
    WorkingDir: "{app}\docs"

Name: "{group}\Release Notes"; \
    Filename: "{app}\docs\ReleaseNotes.md"; \
    WorkingDir: "{app}\docs"

Name: "{group}\Uninstall {#MyAppName}"; \
    Filename: "{uninstallexe}"

Name: "{autodesktop}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"; \
    Comment: "{#MyAppDescription}"; \
    Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; \
    Description: "Launch {#MyAppName}"; \
    WorkingDir: "{app}"; \
    Flags: nowait postinstall skipifsilent

Filename: "{app}\docs\QuickStart.md"; \
    Description: "Open the Quick Start Guide"; \
    WorkingDir: "{app}\docs"; \
    Flags: shellexec postinstall skipifsilent unchecked

[Code]
const
  BrandPurple = $00881131;
  BrandBlue = $00FFA400;
  BrandText = $00402018;

procedure ApplyBrandTypography;
begin
  WizardForm.Caption := '{#MyAppName} Setup';

  WizardForm.WelcomeLabel1.Font.Name := 'Georgia';
  WizardForm.WelcomeLabel1.Font.Size := 17;
  WizardForm.WelcomeLabel1.Font.Style := [fsBold, fsItalic];
  WizardForm.WelcomeLabel1.Font.Color := BrandPurple;

  WizardForm.WelcomeLabel2.Font.Name := 'Segoe UI';
  WizardForm.WelcomeLabel2.Font.Size := 10;
  WizardForm.WelcomeLabel2.Font.Color := BrandText;

  WizardForm.FinishedHeadingLabel.Font.Name := 'Georgia';
  WizardForm.FinishedHeadingLabel.Font.Size := 17;
  WizardForm.FinishedHeadingLabel.Font.Style := [fsBold, fsItalic];
  WizardForm.FinishedHeadingLabel.Font.Color := BrandPurple;

  WizardForm.FinishedLabel.Font.Name := 'Segoe UI';
  WizardForm.FinishedLabel.Font.Size := 10;
  WizardForm.FinishedLabel.Font.Color := BrandText;

  WizardForm.PageNameLabel.Font.Name := 'Georgia';
  WizardForm.PageNameLabel.Font.Size := 12;
  WizardForm.PageNameLabel.Font.Style := [fsBold, fsItalic];
  WizardForm.PageNameLabel.Font.Color := BrandPurple;

  WizardForm.PageDescriptionLabel.Font.Name := 'Segoe UI';
  WizardForm.PageDescriptionLabel.Font.Color := BrandText;

  WizardForm.BeveledLabel.Font.Name := 'Segoe UI';
  WizardForm.BeveledLabel.Font.Style := [fsBold];
  WizardForm.BeveledLabel.Font.Color := BrandBlue;
end;

procedure InitializeWizard;
begin
  ApplyBrandTypography;
end;
