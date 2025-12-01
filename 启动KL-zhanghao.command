#!/usr/bin/env bash
# macOS双击启动文件
# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 执行主启动脚本
bash "$SCRIPT_DIR/start.sh"
