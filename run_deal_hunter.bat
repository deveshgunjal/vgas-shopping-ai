@echo off
title VGAS Deal Hunter - Running
color 0B

echo ============================================================
echo   VGAS WORLD DEAL HUNTER
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking dependencies...
pip install -r requirements.txt -q 2>nul
echo.

echo [2/3] Initializing database...
python -c "from backend.app.database import init_db; init_db()"
echo.

echo [3/3] Starting Deal Hunter...
python sam_world_hunter.py

echo.
echo Results saved to: vgas_world_deals.json
pause
