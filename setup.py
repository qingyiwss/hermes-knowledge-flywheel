#!/usr/bin/env python3
"""NΞXUS 快速部署 — 跨平台安装脚本。用法: python setup.py"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

HOME = Path.home()
OS = platform.system()  # Windows / Darwin / Linux

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
        run(f"{sys.executable} -m pip install {dep} -q", capture_output=True)
    print("✅ psutil + pyyaml")

def clone_flywheel():
    step("克隆飞轮知识库")
    target = HOME / "nexus-knowledge"
    if target.exists():
        print(f"⚠️  目录已存在: {target}")
        return target
    run(f'git clone https://github.com/qingyiwss/hermes-knowledge-flywheel.git "{target}"')
    print(f"✅ 飞轮库 → {target}")
    return target

def setup_nexus_monitor():
    step("部署 Nexus 监控系统")
    nexus_dir = HOME / "nexus"
    nexus_dir.mkdir(exist_ok=True)

    # 写入默认配置
    config = """# NΞXUS 监控配置
agents:
  - name: "MyAgent"
    emoji: "🤖"
    processes: ["python.exe"] if {os} == "Windows" else ["python3"]
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
""".format(os=OS)
    (nexus_dir / "config.yaml").write_text(config, encoding="utf-8")

    # 从飞轮库复制监控脚本（如果有的话）
    print(f"✅ Nexus 配置 → {nexus_dir}/config.yaml")
    print(f"⚠️  Nexus 核心脚本需从飞轮库获取或手动创建")
    return nexus_dir

def setup_obsidian_vault(knowledge_dir):
    step("初始化知识库")
    vault = knowledge_dir
    # 确保关键文件存在
    for f in ["wiki/hot.md", "growth-log.md", "index.md", "lessons-learned.md", "recent-sessions.md"]:
        path = vault / f
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# {path.stem}\n\n", encoding="utf-8")
    print(f"✅ 知识库 → {vault}")

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
    tools = {}
    for name, cmd in [("git", "git --version"), ("node", "node --version"),
                       ("ollama", "ollama --version"), ("python", f"{sys.executable} --version")]:
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            tools[name] = r.stdout.strip() if r.returncode == 0 else None
        except:
            tools[name] = None

    for name, version in tools.items():
        status = f"✅ {version}" if version else "❌ 未安装"
        print(f"  {name}: {status}")

    return tools

def print_next_steps(knowledge_dir, nexus_dir):
    step("部署完成！下一步")
    print(f"""
  1. 启动知识上下文:
     cd "{knowledge_dir}" && python context-loader.py

  2. 部署 Nexus 监控(可选):
     cd "{nexus_dir}"
     # 从飞轮库复制 nexus-watch.py 和 nexus-server.py
     # python nexus-watch.py &
     # python nexus-server.py &
     # 浏览器打开 http://127.0.0.1:8765

  3. 安装本地模型(可选):
     {"winget install Ollama.Ollama" if OS == "Windows" else "curl -fsSL https://ollama.com/install.sh | sh"}
     ollama pull qwen2.5-coder:14b

  4. AI 启动:
     读 BOOTSTRAP.md → 运行 context-loader.py → 开始工作
""")

def main():
    print("""
  ╔═══════════════════════════════════╗
  ║   NΞXUS AI 部署向导              ║
  ║   OS: {os:<26} ║
  ╚═══════════════════════════════════╝
""".format(os=OS))

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
