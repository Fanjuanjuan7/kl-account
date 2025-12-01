@echo off
REM Windows双击启动文件
REM 设置UTF-8编码
chcp 65001 > nul

REM 获取脚本所在目录
cd /d "%~dp0"

REM 执行PowerShell启动脚本
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"

REM 暂停以查看错误信息
if errorlevel 1 (
    echo.
    echo 按任意键退出...
    pause > nul
)
