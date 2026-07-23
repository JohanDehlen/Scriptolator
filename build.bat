@echo off
setlocal

echo Compiling Scriptolator...

.venv\Scripts\python.exe -m compileall -q src\scriptalator

if errorlevel 1 (
    echo.
    echo Scriptolator compilation failed.
    pause
    exit /b 1
)

echo.
echo Scriptolator compiled successfully.
pause

endlocal