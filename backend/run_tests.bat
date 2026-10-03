@echo off
title 🔱 SAM AI Engine Hub - Phase 1 Tests 🔱
echo.
echo ========================================
echo  🔱 PHASE 1 TEST RUNNER 🔱
echo  Master: Vikas Gunjal (Universal King)
echo ========================================
echo.

cd /d "%~dp0"

echo ⚠️  Make sure the server is running first!
echo    (Run start_server.bat in another window)
echo.
echo 🌐 Server URL: http://localhost:8000
echo.
pause

echo.
echo ========================================
echo  Running Phase 1 Advanced Tests...
echo ========================================
echo.

python phase1_test.py

echo.
echo ========================================
echo  Tests Complete!
echo ========================================
echo.
pause