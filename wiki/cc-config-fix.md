---
id: 20260612-cc-config-fix
title: CC 配置修复 — 更新后 token 丢失 + Hermes 包装脚本
tags: [cc, hermes, configuration, fix]
date_created: 2026-06-12
confidence: high
---

## 🎯 问题

CC (Claude Code) 在 Hermes `v0.15.x → v0.16.0` 更新后 token 丢失。

## 🔧 修复

1. **token 注入**：`.env` 中的 `ANTHROPIC_AUTH_TOKEN` 被更新重置，需要重新注入
2. **sed 截断陷阱**：用 `sed -i "s|old|$TOKEN|"` 时，如果 token 含特殊字符可能会被截断
3. **验证方法**：通过检查 token 前缀（前 10 位）确认完整性

## 💡 经验

- 更新 Hermes 后必须验证 CC 是否还能正常工作——因为更新会重写 `.env` 或重置环境
- CC 恢复步骤：`source /root/.hermes/.env` → 运行一次 `claude -p "你是谁"` → 检查输出
