@echo off
REM KL-zhanghao 一键启动脚本 (Windows CMD)
REM 支持双击运行，自动处理路径和虚拟环境

chcp 65001 > nul
setlocal enabledelayedexpansion

REM 获取脚本所在目录并切换到该目录
cd /d "%~dp0"

echo ================================================
echo   KL-zhanghao 可灵AI账号批量注册工具
echo ================================================
echo.
echo 工作目录: %CD%
echo.

REM 检查Python版本
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python
    echo 请先安装Python 3.10或更高版本
    echo.
    echo 按任意键退出...
    pause > nul
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python版本: %PYTHON_VERSION%

REM 检查虚拟环境
if not exist ".venv" (
    echo.
    echo [提示] 首次运行，正在创建虚拟环境并安装依赖...
    echo [等待] 这可能需要几分钟时间，请稍候...
    echo.
    
    REM 运行安装脚本
    call "%~dp0scripts\install.bat"
    
    if errorlevel 1 (
        echo.
        echo [错误] 安装失败，请检查错误信息
        echo.
        echo 按任意键退出...
        pause > nul
        exit /b 1
    )
    
    echo.
    echo [OK] 安装完成！
    echo.
)

REM 激活虚拟环境
echo [提示] 激活虚拟环境...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [OK] 虚拟环境已激活
) else (
    echo [错误] 虚拟环境未找到
    echo 请删除.venv目录后重新运行此脚本
    echo.
    echo 按任意键退出...
    pause > nul
    exit /b 1
)

REM 启动GUI程序
echo.
echo [启动] 启动GUI程序...
echo ================================================
echo.

REM 使用python -m确保模块正确导入
python -m src.app.main

set EXIT_CODE=%errorlevel%

echo.
if %EXIT_CODE% equ 0 (
    echo [OK] 程序正常退出
) else (
    echo [错误] 程序异常退出 (退出码: %EXIT_CODE%^)
    echo.
    echo 按任意键退出...
    pause > nul
)

exit /b %EXIT_CODE%
