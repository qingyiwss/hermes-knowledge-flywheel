#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""会话上下文加载器v2 — 输出极简摘要（~300 tok）。"""

import json, os, sys
from pathlib import Path
from datetime import datetime

# 自动探测 Vault 路径：先看环境变量，再看 Windows 默认位置，最后用脚本所在目录
VAULT = Path(os.environ.get("WIKI_PATH", ""))
if not VAULT.is_dir():
    VAULT = Path.home() / "Documents/Obsidian Vault"
if not VAULT.is_dir():
    VAULT = Path(__file__).resolve().parent
if not VAULT.is_dir():
    print(f"ERROR: 找不到 Vault 目录。请设置 WIKI_PATH 或将脚本放在仓库根目录。", file=sys.stderr)
    exit(1)

def main():
    index = json.loads((VAULT / "wiki-index.json").read_text(encoding="utf-8"))
    hot = (VAULT / "wiki/hot.md").read_text(encoding="utf-8")

    # 紧凑格式
    print(f"// Session {datetime.now():%m-%d %H:%M} | Wiki:{len(index)}notes | D:/nexus D:/Reasonix")

    # P1任务
    p1 = [l.strip()[6:] for l in hot.split("\n") if "P1:" in l]
    print(f"P1: {' | '.join(p1)}" if p1 else "")

    # 最近成果
    recent_lines = [l.strip("- ").strip() for l in hot.split("\n") if l.strip().startswith("- ") and not l.strip().startswith("- P")]
    if recent_lines:
        print("Recent:", "; ".join(recent_lines[:3]))

    # 标签统计(只列标签名+笔记数，不列具体笔记)
    tag_counts = {}
    for v in index.values():
        for tag in v.get("tags", []):
            tag = tag.strip()
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    print(f"Tags: {', '.join(f'{k}:{v}' for k,v in sorted(tag_counts.items()))}")

    # 笔记速查表（极简: 文件名+标题前20字）
    print("Notes: ", end="")
    entries = []
    for k, v in sorted(index.items()):
        title = v.get("title", k)[:20]
        entries.append(f"{k}={title}")
    print(" | ".join(entries))

if __name__ == "__main__":
    main()
