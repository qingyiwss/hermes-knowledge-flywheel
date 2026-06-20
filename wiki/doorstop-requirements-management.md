---
id: 20260529-doorstop
title: Doorstop — 基于 Git 的轻量需求管理
tags: [skill-learning, requirements, cli, git-native, devops]
source_url: https://github.com/doorstop-dev/doorstop
date_created: 2026-05-29
updated: 2026-05-29
last_updated: 2026-05-29
---

## 🎯 核心痛点与应用场景

**痛点：** 需求文档与代码割裂——PRD 在 Wiki/Word 里，代码在 Git 里，两者永远不同步。需求变更时找不到对应代码，代码改动时不知道影响了哪些需求。

**Doorstop 方案：** 把每条需求存为独立 YAML 文件，和代码放在同一个 Git 仓库。需求即代码，版本控制天然覆盖。

**核心场景：**
- 小团队（<20人）用 Git 管理需求，不需要 Jira/Confluence
- 需求追溯矩阵自动生成（什么需求对应什么测试）
- CI 里跑 `doorstop` 检查需求完整性

## 🛠️ 底层原理解析

**数据模型：** 每条需求 = 一个 `XXX-001.yml` 文件
```yaml
active: true
derived: false
level: 1.0
links: []
normative: true
ref: ''
reviewed: null
text: |
  系统应支持用户通过邮箱和密码登录
```

**三层层级：**
```
Document Tree（文档树）
  └─ SRD（需求文档 /reqs/srd）
       ├─ SRD001.yml   ← 顶层需求
       ├─ SRD002.yml
       └─ SRD003.yml
  └─ HLTC（高层测试 /tests/hl，parent=SRD）
       ├─ HLTC001.yml  ← links: [SRD002]  追溯链
       └─ HLTC002.yml
```

**核心机制：**
- `doorstop create DOC ./path` — 创建文档
- `doorstop add DOC` — 交互式添加需求（$EDITOR 编辑 YAML）
- `doorstop link CHILD_ITEM PARENT_ITEM` — 建立追溯关系
- `doorstop publish all ./output` — 导出 HTML/PDF
- `doorstop` 裸命令 — CI 友好的健康检查（追溯完整性）

**Git 集成天然：** 需求分散为 YAML 文件 → `git diff` 看到需求变更 → `git blame` 看到谁改的 → `git merge` 自动合并需求改动。

## 🔄 Hermes 进化映射 (Integration Roadmap)

**对 Nexus 监控/任务系统的启发：**
- 每条 task 可存为 JSON/YAML 文件，放入 `.nexus/items/`
- `nexus link` 建立 task→PR→commit 追溯链
- `nexus publish` 导出任务报告

**可直接落地的点：**
- 我们的监控面板 task 数据已经用了类似格式（`.team_status.json` 中的 history 数组）
- 升级方向：每条 task 独立文件 + 追溯关系 + `nexus check` CI 命令
- 对接 A2A 协议：doorstop 的需求格式可作为 Agent 间传递 task 的标准载体

**相关笔记：** [[a2a-protocol]]、[[nexus-monitor-design]]
