# Wiki Schema

## Domain
Hermes 知识飞轮：AI/NΞXUS 系统能力、多 Agent 框架、Token 优化、工具集成、外贸、量化、游戏。

## 目录结构
```
wiki/           — 所有知识页面（统一目录）
growth-log.md   — 进化日志（只追加）
lessons-learned.md — 经验教训（只追加）
index.md        — 人类可读分类目录
BOOTSTRAP.md    — 基因注入文件
SCHEMA.md       — 本文件
```

## Conventions
- 文件名：小写连字符，如 `token-optimization.md`
- 每个 wiki 页面带 YAML frontmatter
- 使用 `[[wikilinks]]` 互相链接，每页至少 2 个出链
- 更新页面必须更新 `updated` 日期
- 新页面必须添加到 `index.md` 对应分类
- 每次操作记录到 `growth-log.md`
- 含 3+ 来源的页面，段落末尾加 `^[raw/xxx]` 来源标记

## Frontmatter
```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [见下方分类]
sources: [raw/articles/source-name.md]
confidence: high | medium | low
---
```

## Tag Taxonomy

| 分类 | 标签 | 说明 |
|------|------|------|
| NΞXUS 核心 | `nexus` `architecture` | 双引擎、角色分工、防作弊 |
| 多 Agent | `multi-agent` `framework` | AutoGen/CrewAI/LangGraph/MetaGPT |
| CC 集成 | `cc` `integration` | Claude Code 配置、调试 |
| Token 优化 | `token` `optimization` `cache` | 消耗优化、缓存、上下文管理 |
| 工具 | `tool` `platform` `mcp` | MCP/ACI/LiteLLM/Harbor |
| 安全 | `security` `review` | 代码审查、渗透测试 |
| 网络 | `network` `search` | 搜索引擎、浏览器自动化 |
| 外贸 | `trade` `market` | 选品、市场调研、认证 |
| 量化 | `quant` `backtest` | 策略、回测 |
| 游戏 | `game` | 游戏经济学 |
| 视频 | `video` `ai-video` | AI 短视频制作 |
| 小说 | `novel` `ai-novel` | AI 小说引擎 |
