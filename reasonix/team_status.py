#!/usr/bin/env python3
"""
团队状态更新脚本 v2.0 — 增强版
用法: python team_status.py <member> <status> <task> <detail> [options]
  --cost <float>      添加费用（美元）
  --files <int>       修改文件数
"""

import json
import sys
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, ".team_status.json")

VALID_MEMBERS = {"hermes", "cc", "re"}
VALID_STATUSES = {"idle", "working", "done", "error"}


def load_state():
    if not os.path.exists(JSON_PATH):
        return {
            "members": {
                m: {"status": "idle", "task": "", "detail": "", "started": None,
                    "history": [], "total_cost": 0.0, "total_tasks": 0, "total_files": 0}
                for m in VALID_MEMBERS
            }
        }
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        # 补全旧数据缺少的字段
        for m in VALID_MEMBERS:
            if m not in data["members"]:
                data["members"][m] = {"status": "idle", "task": "", "detail": "", "started": None,
                                      "history": [], "total_cost": 0.0, "total_tasks": 0, "total_files": 0}
            mb = data["members"][m]
            for k, v in [("history", []), ("total_cost", 0.0), ("total_tasks", 0), ("total_files", 0)]:
                if k not in mb:
                    mb[k] = v
        return data


def save_state(state):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    # 自动刷新面板 HTML（内嵌数据）
    _refresh_dashboard(state)


def _refresh_dashboard(state):
    """把最新状态嵌入 dashboard HTML，替换 DATA_SENTINEL 标记之间的数据"""
    dash_path = os.path.join(SCRIPT_DIR, "team_dashboard.html")
    if not os.path.exists(dash_path):
        return
    with open(dash_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 提取每个 member 的紧凑数据
    compact = {}
    for m in VALID_MEMBERS:
        mb = state["members"][m]
        compact[m] = {
            "status": mb["status"], "task": mb["task"], "detail": mb["detail"],
            "started": mb["started"], "history": mb["history"],
            "total_cost": mb["total_cost"], "total_tasks": mb["total_tasks"],
            "total_files": mb["total_files"]
        }
    data_json = json.dumps(compact, ensure_ascii=False)

    # 找 DATA_SENTINEL ... DATA_SENTINEL_END 之间的内容并替换
    marker_start = "/* ↓ DATA_SENTINEL"
    marker_end   = "/* ↑ DATA_SENTINEL_END ↑ */"
    start_idx = html.index(marker_start)
    end_idx   = html.index(marker_end) + len(marker_end)

    new_block = f"/* ↓ DATA_SENTINEL — team_status.py 自动替换此注释和下一行的 JSON ↓ */\nwindow.__DATA__ = {data_json};\n/* ↑ DATA_SENTINEL_END ↑ */"
    html = html[:start_idx] + new_block + html[end_idx:]

    with open(dash_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    args = sys.argv[1:]
    if len(args) < 4:
        print(f"用法: python {os.path.basename(__file__)} <member> <status> <task> <detail> [--cost X] [--files N]")
        print(f"  member: {' / '.join(sorted(VALID_MEMBERS))}")
        print(f"  status: {' / '.join(sorted(VALID_STATUSES))}")
        sys.exit(1)

    member = args[0].lower()
    status = args[1].lower()
    task = args[2]
    detail = args[3]

    cost = 0.0
    files_changed = 0
    i = 4
    while i < len(args):
        if args[i] == "--cost" and i + 1 < len(args):
            cost = float(args[i + 1]); i += 2
        elif args[i] == "--files" and i + 1 < len(args):
            files_changed = int(args[i + 1]); i += 2
        else:
            i += 1

    if member not in VALID_MEMBERS:
        print(f"错误: 无效成员 '{member}'，可选: {', '.join(sorted(VALID_MEMBERS))}")
        sys.exit(1)

    if status not in VALID_STATUSES:
        print(f"错误: 无效状态 '{status}'，可选: {', '.join(sorted(VALID_STATUSES))}")
        sys.exit(1)

    state = load_state()
    mb = state["members"][member]
    prev_status = mb.get("status", "idle")

    mb["status"] = status
    mb["task"] = task
    mb["detail"] = detail

    if status == "working" and prev_status != "working":
        mb["started"] = datetime.now(timezone.utc).isoformat()

    # 任务完成时记录历史
    if status in ("done", "error") and prev_status == "working":
        elapsed = ""
        if mb.get("started"):
            start = datetime.fromisoformat(mb["started"])
            delta = datetime.now(timezone.utc) - start
            elapsed = f"{delta.total_seconds():.0f}s"
        mb["history"].append({
            "time": datetime.now(timezone.utc).isoformat(),
            "task": task,
            "status": status,
            "elapsed": elapsed,
            "detail": detail,
            "cost": cost,
            "files": files_changed
        })
        mb["total_cost"] += cost
        mb["total_tasks"] += 1
        mb["total_files"] += files_changed
        # 只保留最近 20 条历史
        if len(mb["history"]) > 20:
            mb["history"] = mb["history"][-20:]

    if status == "idle":
        mb["started"] = None

    save_state(state)
    status_map = {"idle": "🟢", "working": "🔵", "done": "🟡", "error": "🔴"}
    print(f"{status_map.get(status, '❓')} {member} → {status} | {task}")
    if mb.get("started") and status != "idle":
        print(f"   开始: {mb['started']}")
    if cost:
        print(f"   费用: ${cost:.4f} | 修改: {files_changed} 文件")


if __name__ == "__main__":
    main()
