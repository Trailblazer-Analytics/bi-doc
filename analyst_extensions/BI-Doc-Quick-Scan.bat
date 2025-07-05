@echo off
REM BI Documentation Tool - Analyst Quick Launcher
REM Provides a simple drag-and-drop interface for Windows users

setlocal enabledelayedexpansion

echo.
echo =====================================
echo   BI Documentation Tool - Quick Scan
echo =====================================
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

REM Check if file was dragged onto the script
if "%~1"=="" (
    echo No file provided. Please drag a BI file onto this script.
    echo.
    echo Supported file types:
    echo   - Power BI files ^(.pbix^)
    echo   - Tableau Workbooks ^(.twb^)
    echo   - Tableau Packaged Workbooks ^(.twbx^)
    echo.
    echo Alternative: Type the full path to your BI file:
    set /p "filepath=Enter file path: "
    if "!filepath!"=="" (
        echo No file specified. Exiting.
        pause
        exit /b 1
    )
    set "inputfile=!filepath!"
) else (
    set "inputfile=%~1"
)

REM Validate file exists
if not exist "%inputfile%" (
    echo ERROR: File not found: %inputfile%
    pause
    exit /b 1
)

REM Get file extension
for %%F in ("%inputfile%") do (
    set "filename=%%~nF"
    set "extension=%%~xF"
    set "filepath=%%~dpF"
)

REM Validate file type
set "valid_file=0"
if /i "%extension%"==".pbix" set "valid_file=1"
if /i "%extension%"==".twb" set "valid_file=1"
if /i "%extension%"==".twbx" set "valid_file=1"

if %valid_file%==0 (
    echo ERROR: Unsupported file type: %extension%
    echo Supported types: .pbix, .twb, .twbx
    pause
    exit /b 1
)

REM Create output directory
set "outputdir=%filepath%BI-Documentation"
if not exist "%outputdir%" mkdir "%outputdir%"

echo Processing BI file...
echo.
echo File: %filename%%extension%
echo Output: %outputdir%
echo.

REM Run the BI documentation tool
echo Starting analysis...
python -m bidoc -i "%inputfile%" -o "%outputdir%" -f all -v

if %errorlevel%==0 (
    echo.
    echo ========================================
    echo   SUCCESS! Documentation Generated
    echo ========================================
    echo.
    echo Output files created in:
    echo %outputdir%
    echo.
    echo Generated files:
    if exist "%outputdir%\%filename%.md" echo   - %filename%.md ^(Markdown documentation^)
    if exist "%outputdir%\%filename%.json" echo   - %filename%.json ^(JSON metadata^)
    echo.

    REM Ask user what they want to do next
    echo What would you like to do?
    echo   1. Open documentation folder
    echo   2. Open Markdown documentation
    echo   3. Open JSON metadata
    echo   4. Exit
    echo.

    choice /c 1234 /m "Choose an option (1-4): "

    if !errorlevel!==1 (
        echo Opening documentation folder...
        explorer "%outputdir%"
    )
    if !errorlevel!==2 (
        if exist "%outputdir%\%filename%.md" (
            echo Opening Markdown documentation...
            start "" "%outputdir%\%filename%.md"
        ) else (
            echo Markdown file not found.
        )
    )
    if !errorlevel!==3 (
        if exist "%outputdir%\%filename%.json" (
            echo Opening JSON metadata...
            start "" "%outputdir%\%filename%.json"
        ) else (
            echo JSON file not found.
        )
    )
    if !errorlevel!==4 (
        echo Goodbye!
    )

) else (
    echo.
    echo ========================================
    echo   ERROR: Documentation Generation Failed
    echo ========================================
    echo.
    echo Common solutions:
    echo   1. Make sure Python is properly installed
    echo   2. Verify the BI file is not corrupted
    echo   3. Check that you have write permissions to the output directory
    echo   4. Try running as Administrator if permission issues persist
    echo.
    echo For technical support, please check the user guide or contact support.
)

echo.
echo Press any key to exit...
pause >nul
