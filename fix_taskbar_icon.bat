@echo off
echo ========================================
echo    Toolskitch Taskbar Icon Fix
echo ========================================
echo.

echo Step 1: Creating ICO file from PNG...
python create_icon.py

echo.
echo Step 2: Clearing Windows Icon Cache...
echo.

echo Stopping Windows Explorer...
taskkill /f /im explorer.exe 2>nul

echo Clearing icon cache files...
del /q "%localappdata%\IconCache.db" 2>nul
del /q "%localappdata%\Microsoft\Windows\Explorer\iconcache*" 2>nul
del /q "%localappdata%\Microsoft\Windows\Explorer\thumbcache*" 2>nul

echo Restarting Windows Explorer...
start explorer.exe

echo.
echo Step 3: Starting Toolskitch with new icon...
echo.

timeout /t 3 /nobreak >nul

echo Starting Toolskitch...
python main.py

echo.
echo Taskbar icon should now be updated!
echo If the icon still doesn't show correctly, try:
echo 1. Restart your computer
echo 2. Run this script again
echo.
pause 