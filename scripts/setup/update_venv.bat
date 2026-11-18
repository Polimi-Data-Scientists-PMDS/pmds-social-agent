@echo off
setlocal
set "PROJECT_DIR=%~dp0..\.."
if not exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (
    echo No virtual environment found. Run scripts\setup\create_venv.bat first.
    exit /b 1
)
"%PROJECT_DIR%\.venv\Scripts\python.exe" -m pip install -r "%PROJECT_DIR%\requirements.txt"
if errorlevel 1 exit /b 1
echo Requirements installed in .venv.
