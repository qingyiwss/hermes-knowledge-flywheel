#!/usr/bin/env python3
"""项目健康检查脚本 — 扫描代码库、验证关键文件、输出结构化报告"""

import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

ROOT = Path(r"D:\Reasonix")
JSON_PATH = ROOT / ".team_status.json"
DASHBOARD_PATH = ROOT / "team_dashboard.html"

# ── ANSI 颜色 ──
R = "\033[0m"
B = "\033[1m"
D = "\033[2m"
RED = "\033[91m"
GRN = "\033[92m"
YEL = "\033[93m"
CYN = "\033[96m"
MAG = "\033[95m"

SKIP_DIRS = {
    "node_modules", "__pycache__", ".git", ".claude",
    "dist", ".reasonix", "_kenney", "_tiny", "data", "templates",
}

VALID_MEMBERS = {"hermes", "cc", "re"}
VALID_STATUSES = {"idle", "working", "done", "error"}
MEMBER_FIELDS = {"status", "task", "detail", "started", "history",
                 "total_cost", "total_tasks", "total_files"}

anomalies = []


def dwidth(s):
    """字符串显示宽度（CJK 字符算 2 列，忽略 ANSI 转义序列）"""
    s = re.sub(r"\033\[[0-9;]*m", "", s)
    w = 0
    for c in s:
        ea = unicodedata.east_asian_width(c)
        w += 2 if ea in ("W", "F") else 1
    return w


def pad_to(s, width):
    """补齐字符串到指定显示宽度"""
    cur = dwidth(s)
    return s + " " * max(0, width - cur)


def fmt_ok(s):
    return f"{GRN}{s}{R}"

def fmt_warn(s):
    return f"{YEL}{s}{R}"

def fmt_err(s):
    return f"{RED}{s}{R}"

def hrule():
    print(f" {D}{CYN}{'─' * 62}{R}")

def row(icon, color, label, value):
    print(f" {color}{icon}{R} {B}{label:<30}{R} {value}")

def box_header(title, subtitle):
    W = 62
    print()
    print(f" {MAG}{B}╔{'═' * W}╗{R}")
    print(f" {MAG}{B}║  {pad_to(f'{B}{title}{R}', W - 2)}{MAG}{B}║{R}")
    print(f" {MAG}{B}║  {pad_to(f'{D}{subtitle}{R}', W - 2)}{MAG}{B}║{R}")
    print(f" {MAG}{B}╚{'═' * W}╝{R}")

# ═══════════════════════════════════════════════════
# 1. 扫描 .py 文件
# ═══════════════════════════════════════════════════
py_count = 0
total_lines = 0
todo_count = 0
fixme_count = 0

for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        if f.endswith(".py"):
            py_count += 1
            try:
                with open(Path(root) / f, "r", encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        total_lines += 1
                        u = line.upper()
                        if "TODO" in u:
                            todo_count += 1
                        if "FIXME" in u:
                            fixme_count += 1
            except Exception:
                pass

if py_count == 0:
    anomalies.append("未找到任何 .py 文件")

# ═══════════════════════════════════════════════════
# 2. 检查 .team_status.json
# ═══════════════════════════════════════════════════
json_ok = False
json_msg = ""

if not JSON_PATH.exists():
    anomalies.append("缺少 .team_status.json")
    json_msg = fmt_err("✗ 文件不存在")
else:
    try:
        raw = JSON_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
        errs = []

        if not isinstance(data, dict):
            errs.append("根节点不是 JSON 对象")
        elif "members" not in data:
            errs.append("缺少 'members' 键")
        else:
            members = data["members"]
            for m in VALID_MEMBERS:
                if m not in members:
                    errs.append(f"缺少成员 '{m}'")
                else:
                    mb = members[m]
                    for field in MEMBER_FIELDS:
                        if field not in mb:
                            errs.append(f"'{m}' 缺少字段 '{field}'")
                    s = mb.get("status", "")
                    if s and s not in VALID_STATUSES:
                        errs.append(f"'{m}' 无效状态值 '{s}'")
                    if "history" in mb and not isinstance(mb["history"], list):
                        errs.append(f"'{m}' history 类型不是数组")

        if errs:
            anomalies.extend(errs)
            json_msg = fmt_warn(f"⚠ 格式问题 ({len(errs)} 项)")
        else:
            json_ok = True
            json_msg = fmt_ok(f"✓ 格式正确 ({len(members)} 个成员)")

    except json.JSONDecodeError as e:
        anomalies.append(f".team_status.json 不是合法 JSON: {e}")
        json_msg = fmt_err(f"✗ JSON 解析失败: {e}")
    except Exception as e:
        anomalies.append(f".team_status.json 读取失败: {e}")
        json_msg = fmt_err(f"✗ 读取错误: {e}")

# ═══════════════════════════════════════════════════
# 3. 检查 team_dashboard.html
# ═══════════════════════════════════════════════════
dash_ok = DASHBOARD_PATH.exists()
if not dash_ok:
    anomalies.append("缺少 team_dashboard.html")
dash_msg = fmt_ok("✓ 存在") if dash_ok else fmt_err("✗ 缺失")

# ═══════════════════════════════════════════════════
# 4. 输出报告
# ═══════════════════════════════════════════════════
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
box_header("Reasonix 项目健康检查报告", now)

print()
print(f" {B}{CYN}▸ Python 代码扫描{R}")
hrule()
row("✓", GRN, "Python 文件数", f"{B}{py_count}{R}")
row("✓", GRN, "总行数", f"{B}{total_lines}{R}")

t_icon, t_color = ("⚠", YEL) if todo_count > 0 else ("✓", GRN)
f_icon, f_color = ("⚠", YEL) if fixme_count > 0 else ("✓", GRN)
row(t_icon, t_color, "TODO 数量", f"{B}{todo_count}{R}")
row(f_icon, f_color, "FIXME 数量", f"{B}{fixme_count}{R}")

print()
print(f" {B}{CYN}▸ 关键文件检查{R}")
hrule()
row("✓" if json_ok else "✗", GRN if json_ok else RED, ".team_status.json", json_msg)
row("✓" if dash_ok else "✗", GRN if dash_ok else RED, "team_dashboard.html", dash_msg)

print()
print(f" {B}{CYN}▸ 异常汇总{R}")
hrule()
if anomalies:
    for i, a in enumerate(anomalies, 1):
        print(f" {RED}{B}#{i}{R} {RED}{a}{R}")
else:
    print(f" {GRN}{B}✓{R} {GRN}未发现任何异常{R}")

print()
if anomalies:
    print(f" {RED}{B}✗ 发现 {len(anomalies)} 个异常 → exit code = 1{R}")
    print()
    sys.exit(1)
else:
    print(f" {GRN}{B}✓ 一切正常 → exit code = 0{R}")
    print()
    sys.exit(0)
