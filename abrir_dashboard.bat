@echo off
setlocal
cd /d "%~dp0"
.venv\Scripts\python.exe scripts\run_dashboard.py %*
if errorlevel 1 pause
