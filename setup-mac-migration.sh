#!/bin/bash
# ============================================================
# Hermes 生态 Mac 迁移脚本 v1.0
# 从 Windows 迁移 Hermes + CC + RE 到 Mac
# 适用: macOS 10.15+ (MBP 2015)
# ============================================================
set -euo pipefail

echo "╔══════════════════════════════════════════════════╗"
echo "║   Hermes 生态 → Mac 迁移脚本                      ║"
echo "║   目标: Hermes + Claude Code + Reasonix           ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ===== 第一步：基础环境 =====
echo ">>> [1/6] 检查基础环境..."

# 安装 Homebrew (如果没装)
if ! command -v brew &>/dev/null; then
    echo "安装 Homebrew (清华源)..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || {
        echo "brew 直连失败，尝试清华源..."
        export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
        export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
        /bin/bash -c "$(curl -fsSL https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/install.git)"
    }
fi

# Python 3.12
if ! python3.12 --version &>/dev/null; then
    echo "安装 Python 3.12..."
    brew install python@3.12
fi

# Node.js (CC 依赖)
if ! command -v node &>/dev/null; then
    echo "安装 Node.js..."
    brew install node
fi

# Git
if ! command -v git &>/dev/null; then
    brew install git
fi

echo "✔ 基础环境就绪"
echo ""

# ===== 第二步：安装 Hermes =====
echo ">>> [2/6] 安装 Hermes Agent..."
if ! command -v hermes &>/dev/null; then
    curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
    echo "✔ Hermes 安装完成"
else
    echo "✔ Hermes 已安装"
fi
echo ""

# ===== 第三步：配置 Hermes =====
echo ">>> [3/6] 配置 Hermes..."
echo ""
echo "⚠️  现在需要手动操作："
echo "   1. 运行 hermes setup，选择 DeepSeek 作为 provider"
echo "   2. 填入你的 DeepSeek API Key"
echo "   3. 模型选 deepseek-v4-pro"
echo ""
echo "   确认完成后按回车继续..."
read -r

# 重要配置
echo "配置自动审批和模型路由..."
hermes config set approvals.mode off
hermes config set agent.max_turns 60
echo "✔ Hermes 配置完成"
echo ""

# ===== 第四步：安装 Claude Code (CC) =====
echo ">>> [4/6] 安装 Claude Code..."

# 检查 Node.js 版本
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 版本需 >= 18，当前: $(node -v)"
    exit 1
fi

# 全局安装 Claude Code
if ! command -v claude &>/dev/null; then
    echo "安装 Claude Code..."
    npm install -g @anthropic-ai/claude-code
    echo "✔ Claude Code 安装完成"
else
    echo "✔ Claude Code 已安装"
fi

# 配置 CC 用 DeepSeek
CC_DIR="$HOME/.claude"
mkdir -p "$CC_DIR"

cat > "$CC_DIR/deepseek-env.sh" << 'EOF'
#!/bin/bash
# DeepSeek → Claude Code 环境变量 (Mac 版)
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_AUTH_TOKEN="${ANTHROPIC_AUTH_TOKEN:-}"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-${ANTHROPIC_AUTH_TOKEN}}"
export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-deepseek-v4-pro}"
export ANTHROPIC_DEFAULT_SONNET_MODEL="${ANTHROPIC_DEFAULT_SONNET_MODEL:-deepseek-v4-pro}"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="${ANTHROPIC_DEFAULT_HAIKU_MODEL:-deepseek-v4-flash}"
echo "[deepseek-env] ✓ DeepSeek API configured (model: $ANTHROPIC_MODEL)"
EOF

cat > "$CC_DIR/hermes-cc.sh" << 'HERMESCC'
#!/bin/bash
# Hermes → CC 调用包装器 (Mac 版)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/deepseek-env.sh"

CLAUDE_BIN="$(which claude)"
MAX_RETRIES=3
TIMEOUT=600
WORKDIR="."

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--dir) WORKDIR="$2"; shift 2 ;;
        -t|--timeout) TIMEOUT="$2"; shift 2 ;;
        *) TASK="$*"; break ;;
    esac
done

cd "$WORKDIR" && "$CLAUDE_BIN" -p "$TASK" --dangerously-skip-permissions 2>&1 | cat
exit ${PIPESTATUS[0]}
HERMESCC

chmod +x "$CC_DIR/hermes-cc.sh" "$CC_DIR/deepseek-env.sh"

cat > "$CC_DIR/settings.json" << 'EOF'
{
  "enabledPlugins": {},
  "permissions": {
    "allow": ["Bash(git *)", "Bash(python *)", "Bash(npm *)", "Bash(claude *)", "Bash(brew *)", "Bash(curl *)", "Bash(mkdir *)", "Bash(cp *)", "Bash(rm *)", "Bash(ls *)", "Bash(cat *)", "Bash(echo *)", "Bash(which *)", "Bash(find *)", "Bash(head *)", "Bash(wc *)", "Bash(chmod *)", "Bash(hermes *)", "Bash(pip *)"],
    "defaultMode": "bypassPermissions"
  }
}
EOF

echo "✔ CC 配置完成"
echo ""

# ===== 第五步：克隆仓库 =====
echo ">>> [5/6] 同步知识库..."

# 技术知识库
if [ ! -d "$HOME/nexus-knowledge" ]; then
    git clone https://github.com/qingyiwss/hermes-knowledge-flywheel "$HOME/nexus-knowledge"
fi
cd "$HOME/nexus-knowledge" && git pull

# 外贸知识库
if [ ! -d "$HOME/trade-knowledge-flywheel" ]; then
    git clone https://github.com/qingyiwss/trade-knowledge-flywheel "$HOME/trade-knowledge-flywheel"
fi
cd "$HOME/trade-knowledge-flywheel" && git pull

echo "✔ 知识库同步完成"
echo ""

# ===== 第六步：Reasonix =====
echo ">>> [6/6] 设置 Reasonix..."

RE_DIR="$HOME/Reasonix"
if [ ! -d "$RE_DIR" ]; then
    mkdir -p "$RE_DIR"
    # 核心脚本会从 Windows 拷贝后推送，暂时创建占位
    echo "# Reasonix 投资回测引擎" > "$RE_DIR/README.md"
fi

echo "✔ Reasonix 目录就绪 (脚本需从仓库同步)"
echo ""

# ===== 完成 =====
echo "╔══════════════════════════════════════════════════╗"
echo "║  迁移完成！                                       ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║  Hermes:  hermes gateway run                    ║"
echo "║  CC:      ~/.claude/hermes-cc.sh -d DIR '任务'  ║"
echo "║  RE:      python3 ~/Reasonix/valuation_dca.py   ║"
echo "║  知识库:  ~/nexus-knowledge + ~/trade-knowledge ║"
echo "╚══════════════════════════════════════════════════╝"

echo ""
echo "⚠️  Git push 命令：如直连失败，需配置代理或 SSH"
echo "⚠️  Windows 上 hermes 停止后执行: hermes gateway stop"
