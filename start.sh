#!/usr/bin/env bash
# KL-zhanghao 一键启动脚本 (macOS/Linux)
# 支持双击运行，自动处理路径和虚拟环境

set -euo pipefail

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "================================================"
echo "  KL-zhanghao 可灵AI账号批量注册工具"
echo "================================================"
echo ""
echo "📁 工作目录: $SCRIPT_DIR"
echo ""

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3"
    echo "请先安装Python 3.10或更高版本"
    echo ""
    echo "按任意键退出..."
    read -n 1
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python版本: $PYTHON_VERSION"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo ""
    echo "📦 首次运行，正在创建虚拟环境并安装依赖..."
    echo "⏳ 这可能需要几分钟时间，请稍候..."
    echo ""
    
    # 运行安装脚本
    bash "$SCRIPT_DIR/scripts/install.sh"
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ 安装失败，请检查错误信息"
        echo ""
        echo "按任意键退出..."
        read -n 1
        exit 1
    fi
    
    echo ""
    echo "✅ 安装完成！"
    echo ""
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
if [ -f ".venv/bin/activate" ]; then
    source ".venv/bin/activate"
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 错误：虚拟环境未找到"
    echo "请删除.venv目录后重新运行此脚本"
    echo ""
    echo "按任意键退出..."
    read -n 1
    exit 1
fi

# 启动GUI程序
echo ""
echo "🚀 启动GUI程序..."
echo "================================================"
echo ""

# 使用python -m确保模块正确导入
python -m src.app.main

# 程序退出后的处理
EXIT_CODE=$?
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 程序正常退出"
else
    echo "❌ 程序异常退出 (退出码: $EXIT_CODE)"
    echo ""
    echo "按任意键退出..."
    read -n 1
fi

exit $EXIT_CODE
