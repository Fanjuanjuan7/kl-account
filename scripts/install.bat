@echo off
REM 自动安装脚本 - Windows CMD版本
setlocal enabledelayedexpansion

echo [1/5] 创建虚拟环境...
python -m venv .venv
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    exit /b 1
)
echo [OK] 虚拟环境创建成功

echo.
echo [2/5] 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败
    exit /b 1
)
echo [OK] 虚拟环境已激活

echo.
echo [3/5] 升级pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [警告] pip升级失败，继续安装...
)

echo.
echo [4/5] 安装Python依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖包安装失败
    exit /b 1
)
echo [OK] Python依赖包安装成功

echo.
echo [5/5] 安装Playwright浏览器 (Chromium)...
python -m playwright install chromium
if errorlevel 1 (
    echo [警告] Playwright浏览器安装失败，程序可能无法正常运行
    echo [提示] 请手动运行: python -m playwright install chromium
)

echo.
echo ================================================
echo   安装完成！
echo ================================================
echo.
echo 虚拟环境位置: .venv
echo 激活命令: .venv\Scripts\activate.bat
echo.

exit /b 0
