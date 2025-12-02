@echo off
REM Windows Double-Click Launcher
REM Sets UTF-8 encoding
chcp 65001 > nul 2>&1

REM Change to script directory
cd /d "%~dp0"

REM Execute main startup script
call "%~dp0start.bat"

REM Pause on error
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause > nul
)
