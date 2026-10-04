@echo off
chcp 65001 >nul
title VGAS Shopping AI Backend
color 0A

cd /d "D:\projects\Vgas Shooping Ai\backend"

:: Use project venv Python if available, otherwise system python
set "PY=%CD%\venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

echo ============================================================
echo   VGAS SHOPPING AI - BACKEND SERVER
echo ============================================================
echo.
echo Starting on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

"%PY%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
