@echo off
setlocal
set "PROJECT_DIR=%~dp0..\.."
if exist "%PROJECT_DIR%\.venv" (
    echo A .venv already exists. Run scripts\setup\update_venv.bat to install requirements.
    exit /b 1
)
where py >nul 2>&1
if %errorlevel% equ 0 (
    py -3 -m venv "%PROJECT_DIR%\.venv"
) else (
    python -m venv "%PROJECT_DIR%\.venv"
)
if errorlevel 1 exit /b 1
"%PROJECT_DIR%\.venv\Scripts\python.exe" -m pip install -r "%PROJECT_DIR%\requirements.txt"
if errorlevel 1 exit /b 1
echo Environment ready. From the project root, activate it with .venv\Scripts\activate.bat
