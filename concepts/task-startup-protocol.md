---
id: 20260531-task-startup-protocol
title: 任务启动协议 — 预算→确认→执行→签名的完整闭环
tags: [hermes, workflow, token-optimization, protocol]
date_created: 2026-05-31
confidence: high
---

## 🎯 WHAT — 问题

之前的问题：说干就干，干完才知道花了多少。480万 token 花出去了才回头算账。

**规则：先报价，后施工。**

## 🛠️ HOW — 三步协议

### 1. 预算方案（每次任务前）

```
## 📋 任务分析
一句话概括

## 📦 方案
- 步骤1: [ME/CC] [flash/pro] 做什么

## 💰 Token 预算
| 步骤 | 执行者 | 模型 | 预估 |
| ... | ... | ... | ~X K |
| 合计 | | | ~XX K |
```

### 2. 用户确认

用户说"开始"/"OK" → 执行。用户说"调整" → 修改方案。**不说"开始"不动手。**

### 3. 任务签名（每次任务后）

```
---
🤖 deepseek-v4-pro | 本次消耗 ~XX K tokens
```

**必须包含模型名称 + token 消耗。不可省略。**

## 🔄 APPLICATION

已写入 `project-commander` skill，所有任务自动触发。

例外：闲聊、单步查询（"现在几点了""帮我搜一下XX"）不需要协议，直接执行。

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初始 | 2026-05-31 | 写入 project-commander skill + 本页知识库 |
