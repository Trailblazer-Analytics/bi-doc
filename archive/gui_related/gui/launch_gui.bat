@echo off
REM BI Documentation Tool - GUI Launcher
REM Simple launcher for the analyst-friendly GUI

echo.
echo ======================================
echo   BI Documentation Tool - Analyst GUI
echo ======================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Starting BI Documentation GUI...
echo.

REM Run the GUI application
python "%~dp0bidoc_gui.py"

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   Error Starting GUI
    echo ========================================
    echo.
    echo Common solutions:
    echo   1. Make sure the BI Documentation Tool is installed
    echo   2. Check that all dependencies are satisfied
    echo   3. Try running: python -m bidoc --help
    echo.
    echo For enhanced features, install optional dependencies:
    echo   pip install -r requirements.txt
    echo.
    pause
)
