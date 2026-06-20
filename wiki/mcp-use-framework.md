---
title: mcp-use — 全栈 MCP 框架拆解
created: 2026-06-02
updated: 2026-06-02
type: concept
tags: [mcp, ai-agent, tool-calling, agent-upgrade]
sources: [github/mcp-use/mcp-use]
confidence: high
---

# mcp-use — 全栈 MCP 框架拆解

**mcp-use** 是全栈 MCP 开发框架（⭐10K，TypeScript+Python），核心创新：**MCP Apps — 带 UI Widget 的工具，ChatGPT/Claude 里直接渲染交互界面。**

## 核心概念：MCP Apps

```
传统 MCP:  LLM ↔ text  ↔ MCP Server
mcp-use:   LLM ↔ Widget ↔ MCP Server
           用户在 ChatGPT 对话框里看到图表/表单/地图
```

- **Server**: 定义 tool + 关联 widget
- **Widget**: React 组件，在 `resources/` 下自动发现
- **跨平台**: 同一套代码在 ChatGPT、Claude、Cursor 中渲染

## 官方模板（13个）

| 模板 | 功能 |
|------|------|
| Chart Builder | 自然语言生成图表 |
| Diagram Builder | 生成/编辑架构图 |
| Slide Deck | 创建幻灯片 |
| Maps Explorer | 地图+标记+地点搜索 |
| Recipe Finder | 菜谱搜索+膳食计划 |
| File Manager | 远程文件浏览 |
| Media Mixer | 图片/音频/PDF 生成 |
| Widget Gallery | UI 组件展示 |

## 开发体验

```typescript
// 一行命令创建项目
npx create-mcp-use-app@latest

// 定义工具 + Widget 关联
server.tool({
  name: "get-weather",
  widget: "weather-display",  // 自动发现 resources/weather-display/widget.tsx
}, async ({ city }) => widget({ props: { city, temp: 22 } }));

// 部署：推 GitHub → Manufact Cloud 自动上线
```

## 与 Hermes MCP 的关系

- Hermes 已内置 `native-mcp` 客户端（支持 stdio/HTTP MCP Server）
- mcp-use 的 Server 可通过 HTTP 暴露 → Hermes 直接注册为工具
- **关键启示**: mcp-use 的 MCP Apps 模式（工具返回 Widget 而非纯文本）是 MCP 协议的下一个进化方向——但目前 Hermes 的微信/终端交互模式不需要 UI Widget
- **借鉴**: `create-mcp-use-app` 的脚手架模式可参考，用于快速生成 Hermes 自定义工具模板

## 结论

mcp-use 解决了 MCP 的"最后一公里"——让工具调用结果不只是文字，而是可交互的 UI。对 Hermes 的启示：MCP Server 脚手架化 + 自动发现。但对当前纯文本交互场景（微信/终端）价值有限。
