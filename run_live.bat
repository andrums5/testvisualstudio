@echo off
setlocal
cd /d %~dp0
set PYTHONUTF8=1
if exist venv\Scripts\python.exe (
  venv\Scripts\python.exe -u test.py live %*
  goto :eof
)
python -u test.py live %*
