#!/bin/bash
# NΞXUS 一键部署 — Linux/macOS
# curl -fsSL https://raw.githubusercontent.com/qingyiwss/hermes-knowledge-flywheel/main/setup.sh | bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════╗"
echo -e "║   NΞXUS AI 部署 — Linux/macOS    ║"
echo -e "╚═══════════════════════════════════╝${NC}"

# ── 检测包管理器 ──
install_pkg() {
    if command -v brew &>/dev/null; then
        brew install "$@"
    elif command -v apt &>/dev/null; then
        sudo apt update && sudo apt install -y "$@"
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y "$@"
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm "$@"
    else
        echo -e "${RED}❌ 未检测到包管理器，请手动安装: $*${NC}"
        exit 1
    fi
}

# ── 检查 Python ──
if ! command -v python3 &>/dev/null; then
    echo -e "${CYAN}📦 安装 Python 3...${NC}"
    install_pkg python3
fi

# ── 检查 Git ──
if ! command -v git &>/dev/null; then
    echo -e "${CYAN}📦 安装 Git...${NC}"
    install_pkg git
fi

# ── SSH 预检 ──
if ! ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -T git@github.com 2>&1 | grep -qi "successfully authenticated"; then
    echo ""
    echo -e "${RED}⚠️  SSH 未连 GitHub，将尝试其他方式${NC}"
    echo "  如需配置 SSH（推荐）:"
    echo "    ssh-keygen -t ed25519 -C \"you@email.com\""
    echo "    cat ~/.ssh/id_ed25519.pub  # 粘贴到 GitHub → Settings → SSH Keys"
    echo ""
fi

# ── 下载并运行 Python 部署脚本 ──
echo -e "${CYAN}🚀 启动部署...${NC}"
python3 -c "
import urllib.request, sys
try:
    exec(urllib.request.urlopen('https://raw.githubusercontent.com/qingyiwss/hermes-knowledge-flywheel/main/setup.py').read())
except Exception as e:
    print(f'❌ 下载失败: {e}')
    print('尝试从本地运行: python3 setup.py')
    sys.exit(1)
"

echo ""
echo -e "${GREEN}✅ 部署完成！${NC}"
echo "  AI 启动: cd ~/nexus-knowledge && python3 context-loader.py"
