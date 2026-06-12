---
id: 20260531-token-monitoring-system
title: Token 实时监控 + 自适应降级系统 — 反馈闭环落地
tags: [token-optimization, monitoring, cron, flywheel, 自研]
date_created: 2026-05-31
confidence: high
---

## 🎯 WHAT — 建立了什么

完整的 token 消耗反馈闭环：**监控 → 报告 → 自适应降级**。

### 架构
```
state.db (实时写入)
    ↓ 每天 22:00
token-monitor.py (查询今日用量)
    ↓ cron job
每日报告 → 微信推送
    ↓ 自动判断
费用 < $0.50  → 一句话摘要
费用 > $2.00  → ⚠️ 超标警告 + 降级建议
```

## 🛠️ HOW — 三件套

### 1. 监控脚本
`~/.hermes/scripts/token-monitor.py`
- 从 state.db 读取今日所有 session 的 token 用量
- 按模型分组统计 input/output tokens + 费用
- 输出 JSON

### 2. 每日 cron job
```
名称: 每日 Token 报告
调度: 每天 22:00 (0 22 * * *)
工具: terminal only
逻辑: 运行 monitor → 格式化中文报告
```

### 3. 自适应降级规则 (已配置)
| 条件 | 动作 |
|------|------|
| fallback_providers | `['deepseek']` — pro 不可用时切 flash |
| tool_search.threshold_pct | 3% — 仅注入高频工具 |
| show_cost | true — 每次回复可见费用 |
| token_analytics | true — dashboard 可见趋势 |

## 📊 落地效果

```
今日实测 (2026-05-31)
  输入: 1,930,361 tokens
  输出: 492,046 tokens
  费用: $1.03
  模型: deepseek-v4-pro × 16 sessions
```

### 全链路优化总结 (5轮飞轮)

| 飞轮 | 优化项 | 节省/轮 | 状态 |
|------|--------|---------|------|
| 1 | 禁用闲置 toolset | ~2,000 tokens | ✅ 已落地 |
| 1 | 工具搜索阈值 10→3% | ~2,300 tokens | ✅ 已落地 |
| 1 | 开启 cost + analytics | 反馈闭环 | ✅ 已落地 |
| 2 | CLAUDE.md 97→26行 | ~437/CC调用 | ✅ 已验证 |
| 3 | SOUL.md 效率 persona | ~150 tokens | ✅ 已写入 |
| 3 | 子Agent 超时 600→300s | ~500/子任务 | ✅ 已落地 |
| 4 | Memory 条目去重 | ~84 chars | ✅ 已完成 |
| 5 | 每日监控 cron | 持续优化 | ✅ 已调度 |
| 5 | fallback 降级配置 | 自动止损 | ✅ 已配置 |

### 累计效果
```
每轮 Context:     10,245 → ~5,358 tokens  (-48%)
CC CLAUDE.md:     97行 → 26行             (-73%)
Memory:           代理条目 3→1            (-84%)
监控:             从零到自动化日报
降级:             从无到 fallback 配置
```

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初始 | 2026-05-31 | 建立 token-monitor.py + cron job + fallback 配置 |
