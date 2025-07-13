@echo off
echo Installing Toolskitch Dependencies...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher and try again
    pause
    exit /b 1
)

echo Python found. Installing dependencies...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install specific versions of PyQt5 and PyQtWebEngine
echo Installing PyQt5 and PyQtWebEngine...
pip install PyQt5==5.15.9
pip install PyQtWebEngine==5.15.6

REM Install other dependencies
echo Installing other dependencies...
pip install requests

echo.
echo Installation completed successfully!
echo You can now run Toolskitch using: python main.py
echo Or double-click run_toolskitch.bat
pause 