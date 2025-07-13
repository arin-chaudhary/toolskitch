@echo off
echo Starting Toolskitch - Customer Perspective Simulator...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the application
echo Starting Toolskitch...
python main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred while running Toolskitch
    pause
) 