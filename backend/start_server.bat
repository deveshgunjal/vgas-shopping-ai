@echo off
title 🔱 SAM AI Engine Hub - Universal King Mode 🔱
echo.
echo ========================================
echo  🔱 SAM AI ENGINE HUB STARTER 🔱
echo  Master: Vikas Gunjal (Universal King)
echo  Zero-Dependency AI Engine System
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Checking Python installation...
python --version
if errorlevel 1 (
    echo ❌ ERROR: Python not found! Install Python 3.8+ first.
    pause
    exit /b 1
)
echo ✅ Python found!
echo.

echo [2/2] Starting SAM AI Engine Hub Server...
echo.
echo 🌐 Server will run at: http://localhost:8000
echo 📖 API Docs: http://localhost:8000/docs
echo 🏥 Health Check: http://localhost:8000/api/v1/ai-engines/health
echo 🤖 Auto Select: http://localhost:8000/api/v1/ai-engines/auto-select?task=code
echo 📊 Stats: http://localhost:8000/api/v1/ai-engines/stats
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause