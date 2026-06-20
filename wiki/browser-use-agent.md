---
title: Browser Use — AI Agent 浏览器交互框架拆解
created: 2026-06-02
updated: 2026-06-02
type: concept
tags: [browser, ai-agent, web-automation, anti-detect, mcp]
sources: [github/browser-use/browser-use]
confidence: high
---

# Browser Use — AI Agent 浏览器交互框架拆解

**Browser Use** 是当前最热门的 AI Agent 浏览器自动化框架（⭐96K，Python），让 LLM 像人一样操作网页。定位：**"告诉电脑做什么，它就去网页上完成"。**

## 核心架构

```
Agent(task="查找仓库star数", llm=ChatBrowserUse(), browser=Browser())
  → LLM 理解任务 → 拆解为浏览器操作序列
  → Playwright 执行点击/输入/滚动
  → 视觉反馈 → LLM 判断下一步
```

- **Browser**: Playwright 封装，支持本地 Chromium / Cloud 远程浏览器
- **Agent**: 任务理解 → 规划 → 执行循环
- **LLM**: 自带 `ChatBrowserUse()` 专用模型（$0.20/M input tokens），也支持 Gemini/Claude/Ollama

## 关键能力

| 能力 | 说明 |
|------|------|
| **表单填写** | 自动填简历、注册、购物车 |
| **Claude Code 集成** | 官方 SKILL.md，CC 可直接操控浏览器 |
| **Cloud Stealth** | 付费云浏览器：代理轮换 + 指纹伪装 + CAPTCHA 解决 |
| **自定义工具** | `@tools.action` 装饰器扩展 Agent 能力 |
| **CLI 模式** | `browser-use open/click/type/screenshot` 持久化浏览器会话 |
| **持久化 Profile** | 复用真实 Chrome profile，保持登录态 |

## 与 Hermes 的关系

- **直接竞争**: browser-use 的目标是"让 Agent 操作浏览器"，和 Hermes 的 browser 工具功能重叠
- **差异化**: browser-use 更侧重任务级自动化（"帮我买 groceries"），Hermes 更侧重信息获取（搜索/抓取）
- **借鉴点**: `real_browser.py` 复用真实 Chrome profile 思路已在我们 chrome-bridge.py 中实现；Cloud Stealth 对标 Browserbase
- **集成路径**: browser-use 提供 Claude Code SKILL.md → 可集成到 NΞXUS CC 层，让 CC 直接操控浏览器做复杂网页任务

## 局限性

- 开源版无 stealth（需 Cloud 付费），单独使用时 CAPTCHA 问题严重
- 需要 LLM 推理每一步操作，token 消耗大（复杂任务可能 10K+ tokens）
- Python asyncio 模型，与 Hermes 的同步工具调用模式不完全匹配

## 结论

browser-use 是 AI 浏览器自动化的标杆项目。对 NΞXUS 的启示：chrome-bridge.py（真 Chrome CDP）已经覆盖了 browser-use 的核心价值（真实浏览器指纹），不需要额外集成。但如果将来要做"Agent 自主完成网页任务"（非搜索类），browser-use 的 Agent 规划循环是更好的模型。
