---
id: 20260531-token-injection-audit
title: Context 注入审计 — 每轮 10K tokens 的浪费结构与优化
tags: [token-optimization, hermes-config, flywheel, 自研]
date_created: 2026-05-31
confidence: high
---

## 🎯 WHAT — 量化结果

每轮 Hermes turn 固定注入 **~10,245 tokens**，20 轮会话累计 204,900 tokens，按 deepseek-v4-pro 价格约 $0.057。

| 注入组件 | Token/轮 | 占比 | 可优化 |
|----------|---------|------|--------|
| **Tool Schemas (~25 工具)** | **8,750** | **85.4%** | ⚠️ 核心浪费 |
| 工具执行强制块 | 500 | 4.9% | ✅ 可压缩 |
| Skills 列表 (~85 个) | 449 | 4.4% | ✅ 可延迟加载 |
| Memory (持久记忆) | 114 | 1.1% | ✅ 可移交 |
| WeChat 平台指示 | 300 | 2.9% | ❌ 不可砍 |
| User Profile | 90 | 0.9% | ❌ 不可砍 |
| Session Intro | 42 | 0.4% | ❌ 不可砍 |

## 🛠️ 浪费根因

### 1. Tool Schemas — 85% 浪费
- 25 个工具全部注入每轮，但实际 90% 的 turn 只用 3-5 个（terminal/file/search/skill_view/write_file）
- `computer_use` 有数十个参数，schema 保守估计 1,500+ tokens
- `browser_*` 系列 9 个工具，几乎从未在微信会话中使用
- `cronjob`/`delegate_task` schema 各 ~800 tokens
- 配置现状：`tool_search.enabled: auto`, `threshold_pct: 10` — 阈值偏高

### 2. Skills 列表 — 85 个技能全量注入
- 常用技能 < 15 个（hermes-agent, claude-code, codex, github-*, terminal-tools）
- 21 个 creative 技能、6 个 gaming 技能从未触发

### 3. 工具执行强制块 — 500 tokens
- "Finishing the job" + "Tool-use enforcement" + "Skills (mandatory)" 三块总计
- 可压缩 50% 而不影响行为

## 🔧 立即可执行的优化

### 优先级 1：禁用闲置 Toolsets（零风险，最大收益）

```bash
hermes tools disable spotify
hermes tools disable homeassistant
hermes tools disable discord
hermes tools disable discord_admin
hermes tools disable feishu_doc
hermes tools disable feishu_drive
hermes tools disable image_gen
hermes tools disable video
hermes tools disable video_gen
```

预估节省：~2,000 tokens/轮（部分 schema 不加载）

### 优先级 2：降低工具搜索阈值

```bash
hermes config set tools.tool_search.threshold_pct 5
```

预估节省：~1,500 tokens/轮（更多工具被过滤）

### 优先级 3：开启成本可见

```bash
hermes config set display.show_cost true
hermes config set dashboard.show_token_analytics true
```

无 token 节省，但建立反馈闭环。

### 优先级 4：Memory 去重

当前 memory 14 条中有 3 条与 skills 内容重叠，应移交。

## 📊 预期总效果

| 优化项 | 节省 token/轮 | 20轮会话节省 |
|--------|-------------|------------|
| 闲置 toolset 禁用 | ~2,000 | ~40,000 |
| 降低搜索阈值 | ~1,500 | ~30,000 |
| 压缩强制块 | ~250 | ~5,000 |
| Memory 去重 | ~50 | ~1,000 |
| **合计** | **~3,800** | **~76,000** |

从 10,245 → **~6,445 tokens/轮**，节省 37%。

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初始 | 2026-05-31 | 量化每轮 context 注入，识别 tool schemas 为 85% 浪费源 |
