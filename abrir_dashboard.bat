@echo off
setlocal
cd /d "%~dp0"
python scripts\run_dashboard.py %*
if errorlevel 1 pause
