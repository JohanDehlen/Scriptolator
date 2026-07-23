#define MyAppName "Scriptolator"
#define MyAppVersion "1.0.0"
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
UsePreviousAppDir=yes

PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

OutputDir=output
OutputBaseFilename=ScriptolatorSetup-{#MyAppVersion}
SetupIconFile=..\src\scriptalator\resources\scriptolator.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

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

[Tasks]
Name: "desktopicon"; \
    Description: "Create a &desktop shortcut"; \
    GroupDescription: "Additional shortcuts:"; \
    Flags: unchecked

[Dirs]
Name: "{app}\output"
Name: "{app}\profiles"
Name: "{app}\projects"
Name: "{app}\logs"
Name: "{app}\recovery"

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

[UninstallDelete]
; Remove temporary and diagnostic data.
; User-created projects, profiles and generated output are preserved.
Type: filesandordirs; Name: "{app}\recovery"
Type: filesandordirs; Name: "{app}\logs"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
