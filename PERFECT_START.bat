@echo off
setlocal EnableExtensions EnableDelayedExpansion
title LiteLLM Proxy Control

set "PROXY_DIR=C:\litellm_proxy"
set "PYTHON_EXE=%PROXY_DIR%\venv\Scripts\python.exe"
set "LOG_FILE=%PROXY_DIR%\server.log"
rem Prevent a global DEBUG=release variable from breaking LiteLLM.
set "DEBUG="

if not exist "%PYTHON_EXE%" (
  echo ERROR: LiteLLM environment was not found:
  echo %PYTHON_EXE%
  pause
  exit /b 1
)

:menu
cls
call :status
echo.
echo =============================================
echo           LiteLLM Proxy Control
echo =============================================
echo.
echo  [1] Start server
echo  [2] Stop server
echo  [3] Quit
echo.
set "choice="
set /p "choice=Select 1, 2, or 3: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto end
echo Invalid choice. Please enter 1, 2, or 3.
ping -n 3 127.0.0.1 >nul
goto menu

:status
set "SERVER_PID="
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":4000 .*LISTENING"') do set "SERVER_PID=%%P"
if defined SERVER_PID (
  echo Server status: RUNNING ^(PID !SERVER_PID!^)
  echo URL: http://127.0.0.1:4000/v1
) else (
  echo Server status: STOPPED
)
exit /b

:start
call :status
if defined SERVER_PID (
  echo.
  echo LiteLLM is already running.
  pause
  goto menu
)

echo.
echo Starting LiteLLM server...
start "LiteLLM Proxy" /B "%PYTHON_EXE%" -m litellm.proxy.proxy_cli --config "%PROXY_DIR%\config.yaml" --port 4000 > "%LOG_FILE%" 2>&1
set /a attempts=0
:wait_for_start
ping -n 2 127.0.0.1 >nul
set /a attempts+=1
call :status
if defined SERVER_PID (
  echo Server started successfully.
  pause
  goto menu
)
if !attempts! LSS 20 goto wait_for_start
echo ERROR: Server did not start. Check "%LOG_FILE%".
pause
goto menu

:stop
call :status
if not defined SERVER_PID (
  echo.
  echo LiteLLM is already stopped.
  pause
  goto menu
)

echo.
echo Stopping LiteLLM server ^(PID !SERVER_PID!^) ...
taskkill /PID !SERVER_PID! /T /F >nul 2>&1
ping -n 3 127.0.0.1 >nul
call :status
if defined SERVER_PID (
  echo ERROR: Server could not be stopped.
) else (
  echo Server stopped successfully.
)
pause
goto menu

:end
endlocal
exit /b 0
