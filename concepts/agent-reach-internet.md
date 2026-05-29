---
id: 20260529-0002
title: Agent Reach — 给 AI Agent 装上互联网之眼
tags: [skill-learning, web-search, agent-tools, internet-access]
source_url: https://github.com/Panniantong/Agent-Reach
date_created: 2026-05-29
confidence: high
---

# Agent Reach — 给 AI Agent 装上互联网之眼

## 🎯 WHAT — 核心问题与原理

**痛点：** AI Agent 能写代码、改文档，但一遇到"帮我上网搜一下"就抓瞎。每个平台（YouTube/Twitter/Reddit/B站/小红书/GitHub）都有各自的障碍—付费 API、IP 封锁、登录墙、数据清洗。

**解决方案：** Agent Reach 是一套预配置的互联网工具链，通过 MCP（Model Context Protocol）集成，Agent 一句话就能获得多平台访问能力。

**架构：**
```
Agent 发指令
  ↓
mcporter（MCP 网关）
  ├─ yt-dlp → YouTube/B站字幕提取
  ├─ rdt-cli → Reddit 搜索
  ├─ twitter-cli → Twitter/X 读取
  ├─ free-api → 免费搜索 API
  ├─ jina-reader → 网页转 Markdown（清除 HTML 噪音）
  └─ rss → RSS 源订阅
```

**关键特性：**
- 完全免费（所有 API 免费）
- Cookie 本地存储，不上传
- `agent-reach doctor` 一键诊断
- 兼容 Claude Code、Cursor、任何能跑命令行的 Agent

## 🛠️ HOW — 关键实现

**安装方式（一句话）：**
```
帮我安装 Agent Reach：https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

**核心命令：**
```bash
agent-reach doctor      # 诊断：哪些通了、哪些不通、怎么修
agent-reach search "关键词"  # 全网语义搜索
agent-reach youtube "视频链接"  # 提取字幕
agent-reach web "URL"   # 网页→Markdown 清洗
agent-reach twitter "用户名"  # 读取推文
agent-reach reddit "关键词"  # Reddit 搜索
```

**支持的平台矩阵：**
| 平台 | 能力 | 是否需要配置 |
|------|------|-------------|
| 🌐 网页 | 读取任意网页 | ❌ |
| 📺 YouTube | 字幕提取+搜索 | ❌ |
| 🔍 全网搜索 | 语义搜索 | ❌ |
| 📡 RSS | 阅读任意源 | ❌ |
| 📦 GitHub | 读公开仓库 | ❌ |
| 🐦 Twitter/X | 读推文 | 需 Cookie |
| 📺 B站 | 字幕提取+搜索 | 需代理（仅服务器） |
| 📖 Reddit | 搜索+读帖 | 需 rdt login |
| 📕 小红书 | 阅读/搜索/发帖 | 需 Cookie |
| 💬 微信公众号 | 搜索+阅读 | ❌ |

## 🔄 APPLICATION — Hermes 集成方案

### 立即可落地的集成路径

**方案 A：作为 Hermes 工具安装**
1. 在 Hermes 环境下安装 agent-reach（`pip install agent-reach` 或按文档安装）
2. agent-reach 以 MCP 方式暴露工具
3. Hermes 通过 MCP 调用，获得 web_search 能力

**方案 B：作为 cc 的子工具**
1. 在 `D:\Reasonix\.claude\` 配置 agent-reach
2. cc 执行代码时需要联网搜索时，直接调 agent-reach
3. 指挥官也可以通过 terminal 直接调

**推荐路径：** 方案 A + B 同时走。让 Hermes 有原生搜索能力，cc 也能用。

### 填补的能力空白
- ❌ → ✅ **web_search**（当前最大短板）
- ❌ → ✅ **YouTube 字幕提取**（内容创作时可用）
- ❌ → ✅ **RSS 监控**（blogwatcher 替代）
- ❌ → ✅ **网页清洗**（Jina Reader 清除 HTML）

### 集成检查清单
- [ ] 在 Hermes 环境安装 agent-reach
- [ ] 配置 MCP 连接
- [ ] 测试 `agent-reach doctor`
- [ ] 创建 `web-search` skill（封装 agent-reach 命令）
- [ ] 更新 `project-commander` 添加联网搜索步骤

**关联技能：** [[ai-commander-system]], [[harness-engineering]], [[hermes-config]]
**改造路径：** 创建新 skill `web-search`，基于 agent-reach 封装统一搜索接口
**预期效果：** 解锁联网搜索能力，飞轮扫描无需依赖 API proxy
