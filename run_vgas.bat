@echo off
title VGAS Shopping AI v3
cd /d "%~dp0"
echo [VGAS v3] Backend on http://localhost:8001
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
pause
