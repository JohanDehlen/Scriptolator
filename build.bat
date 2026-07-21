@echo off
setlocal

echo Compiling Scriptalator...

.venv\Scripts\python.exe -m compileall -q src\scriptalator

if errorlevel 1 (
    echo.
    echo Scriptalator compilation failed.
    pause
    exit /b 1
)

echo.
echo Scriptalator compiled successfully.
pause

endlocal