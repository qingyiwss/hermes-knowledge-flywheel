---
id: 20260531-cc-context-slim
title: CC 上下文瘦身 — CLAUDE.md 从 97 行→35 行的懒加载改造
tags: [token-optimization, claude-code, flywheel, 自研]
date_created: 2026-05-31
confidence: high
---

## 🎯 WHAT — 问题

CLAUDE.md v2.4 = 97 行，每次 `hermes-cc` 调用都重新注入。gstack 技能表独占 65 行 (68%)。

| 部分 | 行数 | chars | 占比 |
|------|------|-------|------|
| 协作协议 | 1-14 | 283 | 12% |
| **gstack 技能表** | **15-80** | **1,613** | **68%** ← 核心浪费 |
| NΞXUS 工具链 | 81-89 | 257 | 11% |
| 知识库 + 环境 | 90-97 | 206 | 9% |

每天 ~10 次 CC 调用 → 7,870 tokens/天仅 CLAUDE.md，其中 5,273 浪费在 gstack 技能表。

## 🛠️ HOW — 懒加载方案

### 策略：压缩引用 + 按需加载

```
之前 (65行):
### 📋 规划阶段
| 技能 | 用途 |
|------|------|
| `/office-hours` | 产品构思 → 重构为清晰方案 |
| `/plan-ceo-review` | CEO 视角——找产品的10星版本 |
... (40+ 技能 × 2列)

之后 (2行):
🧰 gstack: /autoplan /spec /review /qa /ship /cso /guard /context-save 等40+技能。
   详请 → ~/code/claudecode/gstack/ (CC 按需 read 对应 SKILL.md)
```

### 其他瘦身

| 部分 | 原内容 | 优化 | 节省 |
|------|--------|------|------|
| 工具链 | 5 行版本号表 | 1 行 `ruff/black/pytest/prettier/eslint` | ~60 chars |
| 环境 | 3 行 | 1 行 | ~100 chars |
| 协作协议 | 可压缩 | 保留关键 | ~50 chars |

## 🔧 v2.5 精简版

目标 35 行，~350 tokens。CC 仍能正常工作：
- 协作协议保留（核心行为约束）
- gstack 技能名保留（CC 需要知道有什么可用）
- 工具链压缩为单行（CC 自己会 `which`）
- 环境压缩为单行

## 📊 预期效果

```
指标           v2.4      v2.5      节省
─────────────────────────────────────────
行数           97        35         64%
chars         2,362      ~1,100     53%
tokens        787        ~350       56%
每天 10 次    7,870      3,500      56%
每月          236K       105K       131K tokens
```

按 deepseek-v4-flash ($0.14/1M 输入)：月省 $0.018（微小但每个 token 都算数）。

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初始 | 2026-05-31 | 量化 CLAUDE.md 浪费结构，设计懒加载方案 |
