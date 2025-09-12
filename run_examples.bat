@echo off
setlocal
REM Cambia al directorio de este archivo
cd /d %~dp0
REM Ejecuta el runner forzando UTF-8 en procesos hijo
"%~dp0\venv\Scripts\python.exe" -X utf8 scripts\run_examples.py %*
if errorlevel 1 (
  REM Si no hay venv, usa python del sistema
  python -X utf8 scripts\run_examples.py %*
)
