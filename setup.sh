#!/bin/bash
# NΞXUS 一键部署 — Linux/macOS
# curl -fsSL https://raw.githubusercontent.com/qingyiwss/hermes-knowledge-flywheel/main/setup.sh | bash

set -e

echo "╔═══════════════════════════════════╗"
echo "║   NΞXUS AI 部署 — Linux/macOS    ║"
echo "╚═══════════════════════════════════╝"

# 检查 Python
if ! command -v python3 &>/dev/null; then
    echo "❌ 需要 Python 3.10+，正在安装..."
    if command -v apt &>/dev/null; then
        sudo apt update && sudo apt install -y python3 python3-pip git
    elif command -v brew &>/dev/null; then
        brew install python3 git
    else
        echo "请手动安装 Python 3.10+: https://python.org"
        exit 1
    fi
fi

# 检查 Git
if ! command -v git &>/dev/null; then
    echo "❌ 需要 Git，正在安装..."
    sudo apt install -y git 2>/dev/null || brew install git 2>/dev/null
fi

# 运行 Python 部署脚本
python3 -c "
import urllib.request
exec(urllib.request.urlopen('https://raw.githubusercontent.com/qingyiwss/hermes-knowledge-flywheel/main/setup.py').read())
"

echo ""
echo "✅ 部署完成！AI 启动: cd ~/nexus-knowledge && python3 context-loader.py"
