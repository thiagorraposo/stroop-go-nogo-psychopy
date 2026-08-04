@echo off
setlocal
cd /d "%~dp0"
py -3 scripts\setup_env.py
if not errorlevel 1 exit /b 0

python scripts\setup_env.py
if not errorlevel 1 exit /b 0

echo.
echo ERRO: Nao foi possivel executar o Python 3.
echo Instale o Python pelo site oficial: https://www.python.org/downloads/windows/
echo Durante a instalacao, marque "Add python.exe to PATH" e execute setup.bat novamente.
pause
exit /b 1
