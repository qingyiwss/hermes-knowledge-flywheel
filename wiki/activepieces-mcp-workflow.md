---
title: Activepieces — AI 工作流 + MCP 服务端平台拆解
created: 2026-06-02
updated: 2026-06-02
type: concept
tags: [ai-agent, mcp, workflow, automation, no-code]
sources: [github/activepieces/activepieces]
confidence: high
---

# Activepieces — AI 工作流 + MCP 服务端平台拆解

**Activepieces** 是开源 Zapier 替代品（⭐22.5K，TypeScript），**核心差异化卖点：所有 Pieces（集成模块）同时是 MCP Server，可被 Claude/Cursor 直接调用。**

## 核心架构

```
Pieces（TypeScript npm 包）
  → 作为工作流节点：拖拽编排自动化流程
  → 同时作为 MCP Server：暴露给 AI Agent 调用
```

- **280+ Pieces**: Google Sheets、OpenAI、Discord、RSS、Slack 等
- **60% 社区贡献**: 开源生态，npm 发布
- **TypeScript 热重载**: 本地开发 Pieces 实时生效

## 关键能力

| 能力 | 说明 |
|------|------|
| **AI-First 设计** | 原生 AI pieces，AI SDK 辅助构建流程 |
| **MCP 自动暴露** | 每个 Piece 自动生成 MCP Server 端点 |
| **Human-in-the-loop** | 审批节点、延迟执行、人工输入（Chat/Form 界面） |
| **企业级** | 自托管、网络隔离、品牌定制 |
| **版本化 Flow** | 每次修改自动版本管理 |

## 与 NΞXUS 的关系

- **直接价值**: Activepieces 的 280+ Pieces → MCP 自动转换机制，意味着 Hermes 可以通过 MCP 调用任何 Activepieces 已支持的第三方服务
- **场景**: 用 Activepieces 搭建"监控 GitHub issue → 自动指派 → 通知微信"的工作流，Hermes 只需调 MCP
- **竞争/互补**: Activepieces 解决"连接 SaaS"，Hermes 解决"连接本地工具+终端+浏览器"——两者是互补的
- **未采纳原因**: 
  - 需要 Docker 部署（macOS Catalina 不支持）
  - 280+ Pieces 多为国外 SaaS，国内场景覆盖不足
  - 对 NΞXUS 当前阶段（游戏脚本自动化）价值不大

## 结论

Activepieces 是"AI Agent 的 API 网关"——让 LLM 通过 MCP 安全地调用大量第三方服务。对 NΞXUS 远期有价值（如果需要对接多个 SaaS），当前阶段优先级低。
