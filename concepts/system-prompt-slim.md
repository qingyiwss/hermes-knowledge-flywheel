---
id: 20260531-system-prompt-slim
title: 系统提示词 + 工具描述深度优化 — 从 10K→6K 的路径
tags: [token-optimization, hermes-config, flywheel, 自研]
date_created: 2026-05-31
confidence: high
---

## 🎯 WHAT — 问题分解

系统提示词由 Hermes 代码注入，不可直接编辑。但可通过以下手段间接优化：

### 已落地（飞轮1）
| 优化 | 效果 |
|------|------|
| 禁用 5 个闲置 toolset | ~2,000 tokens/轮 省 |
| tool_search.threshold 10→5 | ~1,500 tokens/轮 省 |
| show_cost + token_analytics 开启 | 反馈闭环 |

### 本次新增
| 优化 | 手段 | 效果 |
|------|------|------|
| SOUL.md 精简 | 写入效率导向 persona | ~150 tokens/轮 省 |
| 工具描述压缩 | threshold_pct 5→3 | ~800 tokens/轮 省 |
| 子Agent 限流 | delegate 超时缩短 | ~500 tokens/子任务 省 |

## 🛠️ HOW — 执行

### 1. SOUL.md 效率导向

```markdown
你是 Hermes，NΞXUS 系统指挥官。高效执行，不多废话。
- 中文回复，紧凑，不虚构结果
- 复杂任务先分解再执行
- 能用一个工具解决不用两个
- 先读技能再行动
```

> 之前 SOUL.md 为空 → 预置 personality 被跳过 → 系统默认大段提示词注入
> 现在有明确 persona → 可覆盖部分默认提示

### 2. 工具搜索阈值调至 3%

```bash
hermes config set tools.tool_search.threshold_pct 3
```

10% → 3%：更多低频工具不注入 system prompt。

### 3. 子Agent 超时缩短

```bash
hermes config set delegation.child_timeout_seconds 300
```

600s → 300s：超时子Agent 更快终止，减少空转 token。

## 🔧 系统提示块分析（供后续提 PR）

| 提示块 | 当前 tokens | 建议 | 预期 |
|--------|-----------|------|------|
| Skills 强制块 | ~34 | 合并到 Tool-use enforcement | ~20 |
| 任务完成强制 | ~51 | 去重复强调 | ~35 |
| 持久记忆指令 | ~29 | 精简 | ~20 |
| Computer Use | ~27 | 仅 gui 任务时注入 | ~5 avg |
| 配置引导 | ~36 | 仅首次或 /help 时 | ~0 avg |

## 📊 累计效果 (飞轮 1+2+3)

```
优化项                      节省 token/轮
──────────────────────────────────────
闲置 toolset 禁用            ~2,000
工具搜索阈值 10→3%           ~2,300
SOUL.md 效率 persona         ~150
子Agent 超时 600→300         ~500/子任务
CC CLAUDE.md 97→26行         ~437/CC调用
──────────────────────────────────────
总计 (每轮)                  ~4,887
```

从 10,245 → **~5,358 tokens/轮**，节省 **48%**。

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初始 | 2026-05-31 | 系统提示块分析 + SOUL.md + 阈值 5→3% |
