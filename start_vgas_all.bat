@echo off
chcp 65001 >nul
title VGAS Shopping AI - Master Controller
echo ===================================================
echo   VGAS SHOPPING AI - LAUNCHING ALL SERVICES...
echo   Developed by: Vikas Gunjal
echo ===================================================

set PROJECT_DIR=D:\Sam\Vgas Shooping Ai

:: Use project venv Python if available, otherwise system python
set "PY=%PROJECT_DIR%\backend\venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

echo.
echo [1/4] Installing Backend Dependencies...
cd /d "%PROJECT_DIR%\backend"
if exist requirements.txt (
    "%PY%" -m pip install -r requirements.txt
    "%PY%" -m playwright install chromium
)

echo.
echo [2/4] Installing WhatsApp Bot Dependencies...
cd /d "%PROJECT_DIR%\bot"
if exist package.json (
    call npm install
)

echo.
echo [3/4] Installing Web App Dependencies...
cd /d "%PROJECT_DIR%\web"
if exist package.json (
    call npm install
)

echo.
echo [4/4] Starting All Services...
echo ---------------------------------------------------

:: Start PostgreSQL (Assuming default Windows service name)
net start postgresql 2>nul
:: Start Redis
start "Redis Server" cmd /c "redis-server"

:: Start Backend Server
start "VGAS Backend API" cmd /k "cd /d %PROJECT_DIR%\backend && "%PY%" -m uvicorn app.main:app --reload --port 8000"

:: Start WhatsApp Bot
start "VGAS WhatsApp Bot" cmd /k "cd /d %PROJECT_DIR%\bot && npm start"

:: Start Web App
start "VGAS Web Frontend" cmd /k "cd /d %PROJECT_DIR%\web && npm start"

echo.
echo ✅ ALL SERVICES STARTED SUCCESSFULLY!
echo ===================================================
echo Backend API: http://localhost:8000/docs
echo Web App: http://localhost:3000
echo WhatsApp Bot: Check the Bot terminal to scan QR code
echo ===================================================
echo.
pause
