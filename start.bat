@echo off
echo Starting Folder Scanner...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run install.bat first to set up the application
    echo.
    pause
    exit /b 1
)

REM Check if the main Python file exists
if not exist folder_scanner.py (
    echo ERROR: folder_scanner.py not found
    echo Please ensure all files are in the same directory
    echo.
    pause
    exit /b 1
)

REM Launch the application
echo Launching Folder Scanner GUI...
python folder_scanner.py

REM If the application exits with an error, show the error
if errorlevel 1 (
    echo.
    echo The application encountered an error.
    echo Please check the error messages above.
    echo.
    pause
)
