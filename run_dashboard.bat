@echo off
cd /d "%~dp0"
echo Starting Macro Watchdog Dashboard...
call python -m streamlit run src/dashboard.py --server.address 0.0.0.0
pause
