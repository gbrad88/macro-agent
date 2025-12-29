@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

:: Logging setup
set LOGFILE="%USERPROFILE%\Desktop\macro_agent_launcher.log"
echo =================================================== > %LOGFILE%
echo  Macro Agent Launcher - %DATE% %TIME% >> %LOGFILE%
echo =================================================== >> %LOGFILE%

echo Logging to %LOGFILE%
echo.

:: --- NUCLEAR ISOLATION ---
set PYTHONPATH=
set PYTHONHOME=
set PYTHONNOUSERSITE=1

echo ===================================================
echo  Macro Agent Launcher - Environment Setup
echo ===================================================

:: Check for Python
python --version >> %LOGFILE% 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH. >> %LOGFILE%
    echo Error: Python is not found in your PATH.
    echo Please install Python 3.10+ and add it to PATH.
    goto :error
)

:: Create VENV if missing
if not exist ".venv" (
    echo [1/3] Creating isolated virtual environment...
    echo [INFO] Creating venv... >> %LOGFILE%
    python -m venv .venv >> %LOGFILE% 2>&1
    if !errorlevel! neq 0 goto :error
) else (
    echo [1/3] Virtual environment exists.
)

:: Install Dependencies
echo [2/3] Checking dependencies (this may take a minute)...
echo [INFO] Installing dependencies... >> %LOGFILE%
:: We call pip directly and stream to console AND log is hard in batch, 
:: so we just let it show on console to show progress ("starts to scroll")
:: but if it fails, we capture the error code.
.venv\Scripts\pip install -r requirements.txt --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [ERROR] Pip install failed. Check internet. >> %LOGFILE%
    echo.
    echo [ERROR] Failed to install dependencies.
    goto :error
)

:: Explicitly Force Install python-dotenv (Fix for Issue #1)
echo [INFO] Forcing python-dotenv install... >> %LOGFILE%
.venv\Scripts\pip install python-dotenv --disable-pip-version-check >> %LOGFILE% 2>&1

:: Log Installed Packages for Debugging
echo [INFO] Current Package List: >> %LOGFILE%
.venv\Scripts\pip list >> %LOGFILE% 2>&1

:: Verify Critical Modules
echo [2.5/3] Verifying environment...
echo [INFO] Verifying imports... >> %LOGFILE%
:: We check streamlit specifically. dotenv check is redundant if we forced install but we keep good measure.
.venv\Scripts\python -c "import dotenv; import streamlit; print('Imports successful')" >> %LOGFILE% 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Import check failed. >> %LOGFILE%
    echo [ERROR] Critical modules failed to load.
    echo See %LOGFILE% for details.
    goto :error
)

:: Run App
echo [3/3] Launching Dashboard...
echo [INFO] Launching Streamlit... >> %LOGFILE%
echo ===================================================

.venv\Scripts\streamlit run src/dashboard.py
if %errorlevel% neq 0 (
    echo [ERROR] Streamlit crashed. >> %LOGFILE%
    echo [ERROR] Dashboard exited with error.
    goto :error
)

echo.
echo [INFO] Exiting normally. >> %LOGFILE%
pause
exit /b 0

:error
echo.
echo ===================================================
echo  CRITICAL ERROR OCCURRED
echo ===================================================
echo.
echo Please check the log file on your Desktop:
echo %LOGFILE%
echo.
pause
exit /b 1
