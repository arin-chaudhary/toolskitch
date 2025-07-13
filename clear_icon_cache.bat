@echo off
echo Clearing Windows Icon Cache...
echo.

echo Stopping Windows Explorer...
taskkill /f /im explorer.exe

echo Clearing icon cache...
del /q "%localappdata%\IconCache.db"
del /q "%localappdata%\Microsoft\Windows\Explorer\iconcache*"

echo Restarting Windows Explorer...
start explorer.exe

echo.
echo Icon cache cleared! The taskbar icon should update on next launch.
echo.
pause 