@echo off
rem BOOKSMITH Studio launcher (S0) — see docs/STUDIO_SPEC.md.
rem Binds 127.0.0.1 only; prints (and opens) a tokenized URL. The UTF-8 env
rem below is the standing rule: CJK output must never cp1252-crash a tool.
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
rem Zero-config first run: a fresh copy has no kit_env.json yet -- probe this
rem machine and write one (keyless defaults) before starting the Studio.
if not exist "_tools\kit_env.json" (
  echo [first run] no _tools\kit_env.json yet - configuring this machine via autoconfig...
  python _tools\autoconfig.py
)
python studio\server.py %*
if errorlevel 1 (
  echo.
  echo ***** Studio exited with an error. If imports failed, run: pip install -r requirements-studio.txt *****
  pause
)
