---
title: Reasonix 项目总览
created: 2026-05-29
updated: 2026-05-29
type: entity
tags: [reasonix, backtest, strategy, automation]
confidence: high
---

# Reasonix 项目总览

## 定位
智能投资策略分析平台。核心功能：估值择时定投、10年历史回测。

## 技术栈
- **Node.js** — 核心引擎（backtest_10y.js, valuation_dca.js）
- **Python** — AI仪表盘 + Token监控
- **Electron** — 桌面应用

## 核心工具

| 工具 | 用途 | 运行方式 |
|------|------|----------|
| `valuation_dca.js` | 估值择时定投计算 | `node valuation_dca.js` |
| `backtest_10y.js` | 10年历史回测 | `node backtest_10y.js` |
| `ai_dashboard.py` | AI 系统仪表盘 | `python ai_dashboard.py` → localhost:19880 |
| `ai_cost.py` | Token 消耗监控 | `python ai_cost.py` |
| `reasonix-desktop.exe` | Windows 桌面应用 | 双击运行 |

## 关键路径
```
D:\Reasonix\
├── backtest_10y.js       — 10年历史回测
├── valuation_dca.js      — 估值择时定投
├── ai_dashboard.py       — AI仪表盘
├── reasonix-desktop.exe  — 桌面GUI
├── CLAUDE.md             — Claude Code 项目上下文
└── .claude/rules/        — Claude Code 规则
```

## 相关
- [[ai-commander-system]] — 如何指挥 Claude Code 开发 Reasonix
- [[valuation-dca-strategy]] — 定投策略详解
- [[backtest-10y]] — 回测结果
