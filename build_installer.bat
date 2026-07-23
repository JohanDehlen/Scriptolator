@echo off
setlocal EnableExtensions

cd /d "%~dp0"

set "APP_NAME=Scriptolator"
set "APP_VERSION=1.0.0"
set "SPEC_FILE=installer\Scriptolator.iss"
set "APP_EXE=dist\Scriptolator.exe"
set "OUTPUT_DIR=installer\output"
set "OUTPUT_FILE=%OUTPUT_DIR%\ScriptolatorSetup-%APP_VERSION%.exe"
set "ISCC="

echo.
echo ========================================
echo   %APP_NAME% Installer Build
echo   Version %APP_VERSION%
echo ========================================
echo.

if not exist "%APP_EXE%" (
    echo ERROR: The application executable was not found:
    echo.
    echo   %APP_EXE%
    echo.
    echo Build Scriptolator.exe first with:
    echo.
    echo   .venv\Scripts\python.exe -m PyInstaller --clean --noconfirm Scriptolator.spec
    echo.
    pause
    exit /b 1
)

if not exist "%SPEC_FILE%" (
    echo ERROR: The Inno Setup script was not found:
    echo.
    echo   %SPEC_FILE%
    echo.
    pause
    exit /b 1
)

if exist "%ProgramFiles%\Inno Setup 7\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 7\ISCC.exe"
)

if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)

if not defined ISCC if defined ProgramFiles(x86) if exist "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"
)

if not defined ISCC if defined ProgramFiles(x86) if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
)

if not defined ISCC (
    where ISCC.exe >nul 2>&1
    if not errorlevel 1 (
        for /f "delims=" %%I in ('where ISCC.exe') do (
            if not defined ISCC set "ISCC=%%I"
        )
    )
)

if not defined ISCC (
    echo ERROR: Inno Setup could not be found.
    echo.
    echo Install Inno Setup, then run this file again.
    echo.
    echo Official download:
    echo   https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Application executable:
echo   %APP_EXE%
echo.
echo Inno Setup compiler:
echo   %ISCC%
echo.
echo Building installer...
echo.

"%ISCC%" "%SPEC_FILE%"

if errorlevel 1 (
    echo.
    echo ========================================
    echo   INSTALLER BUILD FAILED
    echo ========================================
    echo.
    echo Review the Inno Setup errors above.
    echo.
    pause
    exit /b 1
)

if not exist "%OUTPUT_FILE%" (
    echo.
    echo ERROR: Inno Setup completed, but the expected installer was not found:
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

start "" explorer.exe "%CD%\%OUTPUT_DIR%"

pause
exit /b 0
