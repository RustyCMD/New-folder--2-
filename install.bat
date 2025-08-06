@echo off
echo ========================================
echo  Folder Scanner - Installation Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo pip found:
pip --version
echo.

REM Upgrade pip to latest version
echo Upgrading pip to latest version...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo Installing required packages...
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo WARNING: Some packages failed to install
        echo The application may still work with built-in Python libraries
        echo.
    ) else (
        echo.
        echo All packages installed successfully!
        echo.
    )
) else (
    echo requirements.txt not found, skipping package installation
    echo The application uses built-in Python libraries and should work without additional packages
    echo.
)

REM Check if tkinter is available (should be built-in)
echo Checking if tkinter is available...
python -c "import tkinter; print('tkinter is available')" 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: tkinter is not available
    echo tkinter should be included with Python by default
    echo You may need to reinstall Python with tkinter support
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo You can now run the application using:
echo   - Double-click start.bat
echo   - Or run: python folder_scanner.py
echo.
pause
