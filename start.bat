@echo off
REM KL-zhanghao Startup Script for Windows
REM Auto-activate virtual environment and launch GUI

REM Set UTF-8 encoding for console and Python
chcp 65001 > nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

echo ================================================
echo   KL-zhanghao Batch Registration Tool
echo ================================================
echo.
echo Working Directory: %CD%
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Please install Python 3.10 or higher
    echo.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python Version: %PYTHON_VERSION%

REM Check virtual environment
if not exist ".venv" (
    echo.
    echo [INFO] First run - Installing dependencies...
    echo [WAIT] This may take a few minutes...
    echo.
    
    REM Create virtual environment
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo.
        echo Press any key to exit...
        pause > nul
        exit /b 1
    )
    
    REM Activate and install
    call .venv\Scripts\activate.bat
    
    echo Upgrading pip...
    python -m pip install --upgrade pip --quiet
    
    echo Installing requirements...
    pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements
        echo.
        echo Press any key to exit...
        pause > nul
        exit /b 1
    )
    
    echo Installing Playwright browsers...
    python -m playwright install chromium
    if errorlevel 1 (
        echo [WARNING] Playwright installation failed
    )
    
    echo.
    echo [OK] Installation complete!
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [OK] Virtual environment activated
) else (
    echo [ERROR] Virtual environment not found
    echo Please delete .venv folder and run again
    echo.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

REM Launch GUI
echo.
echo [START] Launching GUI...
echo ================================================
echo.

python -m src.app.main

set EXIT_CODE=%errorlevel%

echo.
if %EXIT_CODE% equ 0 (
    echo [OK] Program exited normally
) else (
    echo [ERROR] Program exited with code: %EXIT_CODE%
    echo.
    echo Press any key to exit...
    pause > nul
)

exit /b %EXIT_CODE%
