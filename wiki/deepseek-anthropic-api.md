---
id: 20260612-deepseek-anthropic-api
title: DeepSeek Anthropic 兼容 API — Claude Code 云端驱动方案
tags: [cc, deepseek, api-config, nxsus]
date_created: 2026-06-12
confidence: high
---

## 🎯 背景

Claude Code (CC) 原生只支持 Anthropic API，但在云端服务器上可以通过 DeepSeek 的 Anthropic 兼容 API 驱动，无需 Anthropic 账号。

## 🔧 配置

### 6 个关键环境变量

| 变量 | 值 | 说明 |
|------|-----|------|
| `ANTHROPIC_BASE_URL` | `https://api.deepseek.com/anthropic` | 兼容 API 端点 |
| `ANTHROPIC_AUTH_TOKEN` | `sk-xxxx` | DeepSeek API Key |
| `ANTHROPIC_MODEL` | `deepseek-v4-pro` | 主模型 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `deepseek-v4-pro` | 代理 opus 级别 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `deepseek-v4-pro` | 代理 sonnet 级别 |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `deepseek-v4-flash` | 轻量级子模型 |

### .env 配置

```bash
# ~/.hermes/.env
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN=sk-xxxx
ANTHROPIC_MODEL=deepseek-v4-pro
ANTHROPIC_DEFAULT_OPUS_MODEL=deepseek-v4-pro
ANTHROPIC_DEFAULT_SONNET_MODEL=deepseek-v4-pro
ANTHROPIC_DEFAULT_HAIKU_MODEL=deepseek-v4-flash
ANTHROPIC_DEFAULT_SONNET=deepseek-v4-flash
CLAUDE_CODE_SUBAGENT_MODEL=deepseek-v4-flash
CLAUDE_CODE_EFFORT_LEVEL=max
```

### hermes-cc.sh 包装脚本

路径：`/root/code/hermes-cc.sh`

```bash
# 用法
bash /root/code/hermes-cc.sh -d /root/code/<项目> "任务描述"

# 示例
bash /root/code/hermes-cc.sh -d /root/code/trade-knowledge-flywheel "更新 README"
```

### CLAUDE.md — CC 职责说明书

路径：`/root/code/CLAUDE.md`

CC 只做代码相关的事：写代码、重构、修 bug、测试、lint、Git 操作、代码审查。
**不能做**：写知识库、改 Hermes 配置、通信、自作主张扩大范围。

## ⚠️ 注意事项

1. DeepSeek API key 有截断问题——传递时需要用 `sed` 替换 `.env` 文件中的占位符，不能用 `export` 直接设置（shell 会截断）
2. CC 版本 `v2.1.175` 通过 npm 安装，首次使用需要 OAuth 登录一次（不消耗额度），之后 token 缓存在 `~/.claude/`
3. `ANTHROPIC_AUTH_TOKEN` 也可以直接放 `.env`，CC 启动时自动读取
