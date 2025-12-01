# KL-zhanghao 一键启动脚本 (Windows)
# 支持双击运行，自动处理路径和虚拟环境

param(
    [string]$Python = "python"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# 获取脚本所在目录的绝对路径
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  KL-zhanghao 可灵AI账号批量注册工具" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 工作目录: $ScriptDir" -ForegroundColor White
Write-Host ""

# 检查Python版本
try {
    $pythonVersion = & $Python --version 2>&1
    Write-Host "✅ Python版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 错误：未找到Python" -ForegroundColor Red
    Write-Host "请先安装Python 3.10或更高版本" -ForegroundColor Red
    Write-Host ""
    Write-Host "按任意键退出..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# 检查虚拟环境
if (-not (Test-Path ".venv")) {
    Write-Host ""
    Write-Host "📦 首次运行，正在创建虚拟环境并安装依赖..." -ForegroundColor Yellow
    Write-Host "⏳ 这可能需要几分钟时间，请稍候..." -ForegroundColor Yellow
    Write-Host ""
    
    # 运行安装脚本
    try {
        & "$ScriptDir\scripts\install.ps1" -Python $Python
        
        Write-Host ""
        Write-Host "✅ 安装完成！" -ForegroundColor Green
        Write-Host ""
    } catch {
        Write-Host ""
        Write-Host "❌ 安装失败，请检查错误信息" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host ""
        Write-Host "按任意键退出..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
}

# 激活虚拟环境
Write-Host "🔧 激活虚拟环境..." -ForegroundColor White
$venvActivate = ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
    Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
} else {
    Write-Host "❌ 错误：虚拟环境未找到" -ForegroundColor Red
    Write-Host "请删除.venv目录后重新运行此脚本" -ForegroundColor Red
    Write-Host ""
    Write-Host "按任意键退出..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# 启动GUI程序
Write-Host ""
Write-Host "🚀 启动GUI程序..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 使用python -m确保模块正确导入
try {
    & python -m src.app.main
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "✅ 程序正常退出" -ForegroundColor Green
    } else {
        Write-Host "❌ 程序异常退出 (退出码: $exitCode)" -ForegroundColor Red
        Write-Host ""
        Write-Host "按任意键退出..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    
    exit $exitCode
} catch {
    Write-Host ""
    Write-Host "❌ 程序启动失败" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "按任意键退出..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
