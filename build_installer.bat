@echo off
setlocal EnableExtensions

cd /d "%~dp0"

set "APP_NAME=Scriptolator"
set "APP_VERSION=1.0.0"
set "INSTALLER_SCRIPT=installer\Scriptolator.iss"
set "APPLICATION_EXE=dist\Scriptolator.exe"
set "OUTPUT_DIRECTORY=installer\output"
set "OUTPUT_FILE=%OUTPUT_DIRECTORY%\ScriptolatorSetup-%APP_VERSION%.exe"
set "ISCC="

echo.
echo ========================================
echo   %APP_NAME% Installer Build
echo   Version %APP_VERSION%
echo ========================================
echo.

if not exist "%APPLICATION_EXE%" (
    echo ERROR: The packaged application was not found:
    echo.
    echo   %APPLICATION_EXE%
    echo.
    echo Rebuild Scriptolator.exe first:
    echo.
    echo   .venv\Scripts\python.exe -m PyInstaller --clean --noconfirm Scriptolator.spec
    echo.
    pause
    exit /b 1
)

if not exist "%INSTALLER_SCRIPT%" (
    echo ERROR: The Inno Setup script was not found:
    echo.
    echo   %INSTALLER_SCRIPT%
    echo.
    pause
    exit /b 1
)

if not exist "installer\branding\wizard.png" (
    echo ERROR: The tall installer artwork was not found:
    echo.
    echo   installer\branding\wizard.png
    echo.
    echo Generate the artwork with:
    echo.
    echo   .venv\Scripts\python.exe installer\create_installer_assets.py
    echo.
    pause
    exit /b 1
)

if not exist "installer\branding\wizard_small.png" (
    echo ERROR: The installer header artwork was not found:
    echo.
    echo   installer\branding\wizard_small.png
    echo.
    echo Generate the artwork with:
    echo.
    echo   .venv\Scripts\python.exe installer\create_installer_assets.py
    echo.
    pause
    exit /b 1
)

call :FindInnoSetup

if not defined ISCC (
    echo ERROR: Inno Setup could not be found.
    echo.
    echo Install Inno Setup and run this file again.
    echo.
    echo Official download:
    echo   https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Application executable:
echo   %APPLICATION_EXE%
echo.
echo Installer script:
echo   %INSTALLER_SCRIPT%
echo.
echo Inno Setup compiler:
echo   %ISCC%
echo.
echo Building branded installer...
echo.

if exist "%OUTPUT_FILE%" (
    del /q "%OUTPUT_FILE%" >nul 2>&1
)

"%ISCC%" "%INSTALLER_SCRIPT%"

if errorlevel 1 (
    echo.
    echo ========================================
    echo   INSTALLER BUILD FAILED
    echo ========================================
    echo.
    echo Review the Inno Setup compiler output above.
    echo.
    pause
    exit /b 1
)

if not exist "%OUTPUT_FILE%" (
    echo.
    echo ERROR: The compiler finished, but the expected installer
    echo was not created:
    echo.
    echo   %OUTPUT_FILE%
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALLER BUILD SUCCESSFUL
echo ========================================
echo.
echo Installer created:
echo.
echo   %OUTPUT_FILE%
echo.

start "" explorer.exe "%CD%\%OUTPUT_DIRECTORY%"

pause
exit /b 0


:FindInnoSetup

if exist "%ProgramFiles%\Inno Setup 7\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 7\ISCC.exe"
    exit /b 0
)

if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
    exit /b 0
)

if defined ProgramFiles(x86) (
    call set "PROGRAM_FILES_X86=%%ProgramFiles(x86)%%"
)

if defined PROGRAM_FILES_X86 (
    if exist "%PROGRAM_FILES_X86%\Inno Setup 7\ISCC.exe" (
        set "ISCC=%PROGRAM_FILES_X86%\Inno Setup 7\ISCC.exe"
        exit /b 0
    )

    if exist "%PROGRAM_FILES_X86%\Inno Setup 6\ISCC.exe" (
        set "ISCC=%PROGRAM_FILES_X86%\Inno Setup 6\ISCC.exe"
        exit /b 0
    )
)

for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do (
    if not defined ISCC (
        set "ISCC=%%I"
    )
)

exit /b 0
