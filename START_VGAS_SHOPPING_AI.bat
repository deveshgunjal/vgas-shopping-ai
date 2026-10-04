@echo off
title Vgas Shopping AI v3.0 - Total Domination
color 0A

echo ============================================================
echo   VGAS SHOPPING AI v3.0 - Total Domination Edition
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/5] Running Self-Heal...
python self_heal.py
echo.

echo [2/5] Installing Python dependencies...
pip install -r requirements.txt -q 2>nul
echo.

echo [3/5] Setting up database...
python -c "from backend.app.database import init_db; init_db()"
echo.

echo [4/5] Starting Backend (FastAPI - Port 8000)...
start "Vgas Backend" cmd /k "cd /d "%~dp0" && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [5/5] Opening Browser...
start http://localhost:8000

echo.
echo ============================================================
echo   VGAS SHOPPING AI v3.0 - READY!
echo ============================================================
echo.
echo   Backend API:   http://localhost:8000
echo   API Docs:      http://localhost:8000/docs
echo   Dashboard:     http://localhost:8000
echo   Health:        http://localhost:8000/health
echo   Extension:     Load extension/ folder in Chrome
echo.
echo   Deal Hunter:   python sam_world_hunter.py
echo.
echo   Press Ctrl+C to stop.
echo ============================================================
echo.

pause