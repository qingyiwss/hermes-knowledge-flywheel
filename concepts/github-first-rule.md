---
id: 20260531-github-first-rule
title: GitHub First 规则 — 遇难先搜，不重复造轮子
tags: [hermes, workflow, github, protocol]
date_created: 2026-05-31
confidence: high
---

## 🎯 WHAT — 问题

之前的模式：遇到问题 → 自己硬上 → 反复试错 → 浪费 token。
以 crewAI 拆解为例，子Agent 超时 600s 后才补救，其实 GitHub 上早有成熟的 README 分析工具。

**规则：遇到难题先看别人怎么解决的。**

## 🛠️ HOW — 两步流程

### 触发条件（任一满足）

1. 从未处理过的问题
2. 同一问题出错 ≥ 2 次

### 执行流程

```
① 提取关键词 → 搜 GitHub
② 过滤：pushed > 一个月（优先一周内）
③ 看 Top 3 README
④ 有现成方案 → 借鉴适配
   没有        → 再自己干
```

### 硬过滤规则

| 条件 | 动作 |
|------|------|
| 最后更新 > 一个月 | 跳过 |
| 最后更新 ≤ 一周 | 优先 |
| Stars < 50 | 跳过（除非唯一） |

## 🔄 APPLICATION

已写入 `project-commander` skill，所有任务自动遵守。

示例：

```
问题: Python 脚本需要监控文件变化
❌ 自己写 inotify 轮询逻辑
✅ GitHub 搜 "python file watcher" → watchdog (⭐7K, 3天前更新) → pip install
```

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初始 | 2026-05-31 | 写入 project-commander skill + 本页知识库 |
