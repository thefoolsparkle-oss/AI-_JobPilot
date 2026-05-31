@echo off
cd /d "%~dp0backend"

echo === JobPilot - AI Job Search Copilot ===
echo Starting server at http://127.0.0.1:8001
echo.
echo If this is your first time, make sure:
echo   1. .env file has your DEEPSEEK_API_KEY
echo   2. pip install -r requirements.txt has been run
echo.
echo Press Ctrl+C to stop the server.
echo ---------------------------------------

REM Try to find real Python (not MS Store alias)
set PYTHON_CMD=

REM 1. Search in LOCALAPPDATA\Programs\Python (default per-user install on Windows)
for /d %%d in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%d\python.exe" (
        set PYTHON_CMD=%%d\python.exe
        goto found
    )
)

REM 2. Search in C:\Program Files\Python*
for /d %%d in ("C:\Program Files\Python*") do (
    if exist "%%d\python.exe" (
        set PYTHON_CMD=%%d\python.exe
        goto found
    )
)

REM 3. Search in C:\Python*
for /d %%d in ("C:\Python*") do (
    if exist "%%d\python.exe" (
        set PYTHON_CMD=%%d\python.exe
        goto found
    )
)

REM 4. Try 'py' launcher
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
    goto found
)

REM Nothing found
echo ERROR: Python not found.
echo Please install Python from https://www.python.org/downloads/
pause
exit /b 1

:found
echo Using Python: %PYTHON_CMD%
echo.
"%PYTHON_CMD%" -m uvicorn app.main:app --host 127.0.0.1 --port 8001

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start. Possible causes:
    echo   - Dependencies missing: run "pip install -r requirements.txt"
    echo.
)

pause
