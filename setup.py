#!/usr/bin/env python3
"""NΞXUS 快速部署 — 跨平台安装脚本。用法: python setup.py"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

HOME = Path.home()
OS = platform.system()

REPO_SSH = "git@github.com:qingyiwss/hermes-knowledge-flywheel.git"
REPO_HTTPS = "https://github.com/qingyiwss/hermes-knowledge-flywheel.git"


def run(cmd, **kw):
    print(f"  → {cmd}")
    return subprocess.run(cmd, shell=True, **kw)


def step(msg):
    print(f"\n{'='*50}\n  {msg}\n{'='*50}")


def check_python():
    v = sys.version_info
    if v < (3, 10):
        print(f"❌ Python 3.10+ required, got {v.major}.{v.minor}")
        sys.exit(1)
    print(f"✅ Python {v.major}.{v.minor}.{v.micro}")


def install_python_deps():
    step("安装 Python 依赖")
    deps = ["psutil", "pyyaml"]
    for dep in deps:
        r = run(f"{sys.executable} -m pip install {dep} -q", capture_output=True)
        if r.returncode != 0:
            print(f"⚠️  pip install {dep} 失败，尝试 --user 模式...")
            run(f"{sys.executable} -m pip install {dep} --user -q", capture_output=True)
    print("✅ psutil + pyyaml")


def _test_ssh():
    """测试 SSH 能否连 GitHub"""
    r = subprocess.run(
        "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -T git@github.com 2>&1",
        shell=True, capture_output=True, text=True, timeout=8
    )
    # 成功认证返回 "Hi xxx! You've successfully authenticated"
    return "successfully authenticated" in r.stdout.lower() or \
           "successfully authenticated" in r.stderr.lower()


def clone_flywheel():
    step("克隆飞轮知识库")
    target = HOME / "nexus-knowledge"
    if target.exists():
        print(f"⚠️  目录已存在: {target}")
        return target

    # 策略: SSH 优先 → gh CLI → 手动指引
    if _test_ssh():
        url = REPO_SSH
        print("✅ SSH 连接 GitHub 正常，使用 SSH 克隆")
    else:
        # 尝试 gh CLI
        gh = shutil.which("gh")
        if gh:
            print("🔑 SSH 未配置，尝试 gh CLI...")
            r = run(
                f'gh repo clone qingyiwss/hermes-knowledge-flywheel "{target}"',
                capture_output=True, text=True
            )
            if r.returncode == 0:
                print(f"✅ 飞轮库(gh) → {target}")
                return target
            print(f"⚠️  gh clone 失败: {r.stderr.strip()}")

        # 最后尝试 HTTPS + 环境变量 token
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            url = f"https://{token}@github.com/qingyiwss/hermes-knowledge-flywheel.git"
            print("🔑 使用 GITHUB_TOKEN 环境变量")
        else:
            print("\n❌ 无法克隆私有仓库。请选择以下方式之一：\n")
            print("  方式1 (推荐): 配置 SSH Key")
            print("    ssh-keygen -t ed25519 -C \"your@email.com\"")
            print("    cat ~/.ssh/id_ed25519.pub  # 复制到 GitHub → Settings → SSH Keys")
            print("    然后重新运行 python setup.py\n")
            print("  方式2: 使用 GitHub CLI")
            print("    brew install gh && gh auth login")
            print("    然后重新运行 python setup.py\n")
            print("  方式3: 设置 Token 环境变量")
            print("    export GITHUB_TOKEN=ghp_xxxxxxxxxxxx")
            print("    然后重新运行 python setup.py\n")
            print("    然后重新运行 python setup.py\n")
            sys.exit(1)

    r = run(f'git clone "{url}" "{target}"', capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ 克隆失败:\n{r.stderr}")
        sys.exit(1)
    print(f"✅ 飞轮库 → {target}")
    return target


def setup_nexus_monitor():
    step("部署 Nexus 监控系统")
    nexus_dir = HOME / "nexus"
    nexus_dir.mkdir(exist_ok=True)
    win_procs = '["python.exe"]'
    unix_procs = '["python3"]'
    procs = win_procs if OS == "Windows" else unix_procs
    config = f"""# NΞXUS 监控配置
agents:
  - name: "MyAgent"
    emoji: "🤖"
    processes: {procs}
    args_contains: []

server:
  host: "127.0.0.1"
  port: 8765

watch:
  interval: 3

system:
  cpu: true
  memory: true
  disk: true
  network: true
"""
    (nexus_dir / "config.yaml").write_text(config, encoding="utf-8")
    print(f"✅ Nexus 配置 → {nexus_dir}/config.yaml")


def setup_obsidian_vault(knowledge_dir):
    step("初始化知识库")
    for f in ["wiki/hot.md", "growth-log.md", "index.md",
              "lessons-learned.md", "recent-sessions.md"]:
        path = knowledge_dir / f
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# {path.stem}\n\n", encoding="utf-8")
    print(f"✅ 知识库 → {knowledge_dir}")


def setup_git(vault_dir):
    step("配置 Git")
    os.chdir(vault_dir)
    if not (vault_dir / ".git").exists():
        run("git init")
    run('git config user.email "365869914@qq.com"')
    run('git config user.name "qingyiwss"')
    print("✅ Git 已配置")


def detect_tools():
    step("检测可用工具")
    for name, cmd in [("git", "git --version"), ("node", "node --version"),
                       ("ollama", "ollama --version"), ("python", f"{sys.executable} --version")]:
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            status = f"✅ {r.stdout.strip()}" if r.returncode == 0 else "❌ 异常"
        except Exception:
            status = "❌ 未安装"
        print(f"  {name}: {status}")


def print_next_steps(knowledge_dir, nexus_dir):
    step("部署完成！下一步")
    ollama_cmd = "winget install Ollama.Ollama" if OS == "Windows" else \
                 "curl -fsSL https://ollama.com/install.sh | sh"
    print(f"""
  1. 启动知识上下文:
     cd "{knowledge_dir}" && python context-loader.py

  2. 部署 Nexus 监控(可选):
     cd "{nexus_dir}"
     # 从飞轮库复制 nexus-watch.py 和 nexus-server.py
     # 浏览器打开 http://127.0.0.1:8765

  3. 安装本地模型(可选):
     {ollama_cmd}
     ollama pull qwen2.5-coder:14b

  4. AI 启动:
     读 BOOTSTRAP.md → 运行 context-loader.py → 开始工作
""")


def main():
    print(f"""
  ╔═══════════════════════════════════╗
  ║   NΞXUS AI 部署向导              ║
  ║   OS: {OS:<26} ║
  ╚═══════════════════════════════════╝
""")
    check_python()
    install_python_deps()
    knowledge = clone_flywheel()
    setup_obsidian_vault(knowledge)
    setup_git(knowledge)
    nexus = setup_nexus_monitor()
    detect_tools()
    print_next_steps(knowledge, nexus)


if __name__ == "__main__":
    main()
