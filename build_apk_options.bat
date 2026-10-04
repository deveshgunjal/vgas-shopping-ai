@echo off
echo ============================================================
echo   VGAS Shopping AI - APK Build Options for ARM Windows
echo ============================================================
echo.
echo Android Studio ARM Windows वर support नाही.
echo खालील 3 पर्यायांपैकी एक निवडा:
echo.
echo [1] GitHub Actions (Free Cloud Build - Recommended)
echo     - Code GitHub वर push करा
echo     - APK automatically build होईल
echo     - Download करा आणि install करा
echo.
echo [2] Expo EAS Build (iOS + Android दोन्ही - Free)
echo     - expo.dev account लागेल
echo     - Cloud मध्ये APK + AAB build होईल
echo.
echo [3] Appetize.io (Online Android Emulator)
echo     - APK upload करा
echo     - Browser मध्ये Android ऍप test करा
echo.
echo ============================================================
set /p choice="निवड करा (1/2/3): "

if "%choice%"=="1" goto github
if "%choice%"=="2" goto expo
if "%choice%"=="3" goto appetize

:github
echo.
echo GitHub Actions Setup:
echo 1. github.com वर जा आणि account बनवा (free)
echo 2. D:\Sam\Vgas Shooping Ai हा folder upload करा
echo 3. Actions tab मध्ये "Build VGAS Android APK" run करा
echo 4. APK download होईल!
echo.
echo GitHub Repo बनवण्यासाठी: https://github.com/new
pause
exit

:expo
echo.
echo Expo EAS Build Setup:
echo 1. npm install -g eas-cli
echo 2. eas login
echo 3. eas build -p android
echo 4. APK download link मिळेल!
echo.
cd /d "D:\Sam\Vgas Shooping Ai\ios"
echo Expo project folder: %CD%
pause
exit

:appetize
echo.
echo Appetize.io - Online Android Emulator:
echo https://appetize.io/upload
echo APK upload करा आणि browser मध्ये test करा!
pause
exit
