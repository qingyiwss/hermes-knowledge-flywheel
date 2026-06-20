---
id: 20260531-gstack-skill-system
title: gstack — CC 技能体系集成
tags: [claude-code, gstack, skill, tooling]
source_url: https://github.com/garrytan/gstack
date_created: 2026-05-31
updated: 2026-05-31
confidence: high
---

## 🎯 核心认知

gstack 是 YC CEO Garry Tan 的 Claude Code 工具集（⭐104,899），内含 23 个专业角色 + 8 个 power tools，全为 CC slash command / SKILL.md 格式。

一句话：**把 Claude Code 变成一个虚拟工程团队。**

## 📦 已集成技能

| 阶段 | 技能 | 功能 |
|------|------|------|
| 规划 | office-hours, plan-{ceo/eng/design/devex}-review, autoplan, spec | 产品构思→架构锁定→Spec 输出 |
| 实施 | review, investigate, design-review, qa, scrape | Code Review/调试/QA/数据抓取 |
| 发布 | ship, land-and-deploy, canary | 测试→PR→部署→验证 |
| 安全 | careful, freeze, guard, cso | 破坏性操作警告/目录锁定/安全审计 |
| 记忆 | context-save/restore, learn | 跨会话上下文持久化 |

## 🔧 SKILL.md 模板规范

gstack 的 SKILL.md 格式（已适配 NΞXUS）：

```yaml
---
name: skill-name
version: 1.0.0
description: 一句话用途
allowed-tools: [Bash, Read, Write, ...]
triggers: [触发关键词]
---
```

NΞXUS 扩展字段：
- `role: cc | hermes` — 归属引擎
- `knowledge-prereq: [wiki-page]` — 前置知识库页面

## 📊 与 NΞXUS 的对比

| 维度 | gstack | NΞXUS |
|------|--------|-------|
| 角色模型 | 23 个 CC 子角色 | 双引擎(Hermes+CC) |
| 技能格式 | SKILL.md | SKILL.md + Wiki |
| 知识库 | gbrain(外部) | nexus-knowledge(本地) |
| 调度 | CC slash 命令 | Hermes hermes-cc |
| 通信 | CC 内对话 | 微信(Hermes) ⇄ CC |

## 🔗 相关内容

- [[nexus-dual-engine]] — 双引擎协议
- [[github-first-rule]] — GitHub First 规则
- [[claude-obsidian-architecture]] — CC 工作流设计

## 📊 飞轮日志

| 日期 | 操作 |
|------|------|
| 2026-05-31 | 集成 gstack: 克隆到 ~/code/claudecode/gstack/，40+ 技能写入 CLAUDE.md v2.4 |
