@echo off
setlocal
cd /d "%~dp0"

:: --- NUCLEAR ISOLATION ---
set PYTHONPATH=
set PYTHONHOME=
set PYTHONNOUSERSITE=1

echo ===================================================
echo  Macro Agent Launcher - Environment Setup
echo ===================================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not found in your PATH.
    echo Please install Python 3.10+ and check "Add to PATH".
    pause
    exit /b 1
)

:: Create VENV if missing
if not exist ".venv" (
    echo [1/3] Creating isolated virtual environment...
    python -m venv .venv
) else (
    echo [1/3] Virtual environment exists.
)

:: Install Dependencies
echo [2/3] Checking dependencies...
.venv\Scripts\pip install -r requirements.txt -q --disable-pip-version-check

:: Run App
echo [3/3] Launching Dashboard...
echo ===================================================
.venv\Scripts\streamlit run src/dashboard.py

pause
