---
id: 20260529-0003
title: 智能模型路由 — 根据复杂度自动选模型
tags: [skill-learning, model-routing, cost-optimization, agent-upgrade]
source_url: https://github.com/0xrdan/claude-router
date_created: 2026-05-29
confidence: high
---

# 智能模型路由 — 根据复杂度自动选模型

## 🎯 WHAT — 核心问题与原理

**痛点：** 一条"帮我看看这个文件"消耗和"帮我重构整个架构"一样的模型资源。简单查询不该花 strong model 的钱。

**方案：** UserPromptSubmit Hook — 在 Agent 处理请求前，用一个极快的分类器判断复杂度，自动选模型。

**架构：**
```
用户发 prompt
  ↓
UserPromptSubmit Hook 触发 [~0ms]
  ↓
分类器分析 → 简单? haiku : sonnet
  ↓
写入 settings.local.json
  ↓
Agent 用选定模型处理
```

## 🛠️ HOW — 关键实现

### 规则引擎（纯规则，零延迟）

```python
COMPLEX_KW = ["写代码","实现","debug","重构","架构","分析","测试","修复"]
SIMPLE_KW  = ["查","搜","看看","解释","总结"]

if any(kw in prompt for kw in COMPLEX_KW):
    return "sonnet"     # 复杂 → 强模型
if any(kw in prompt for kw in SIMPLE_KW):
    return "haiku"      # 简单 → 便宜模型
if len(prompt) < 50:
    return "haiku"      # 短 → 便宜
if len(prompt) > 300:
    return "sonnet"     # 长 → 强模型
return "sonnet"         # 不确定 → 默认强
```

### Hook 注册

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{"type": "command", "command": "python .claude/hooks/model-router.py"}]
    }]
  }
}
```

### 成本对比

| 任务类型 | 无路由 | 有路由 | 节省 |
|----------|--------|--------|------|
| "帮我看看 README" | sonnet ($3/$15) | haiku ($0.25/$1.25) | **~90%** |
| "重构 auth 模块" | sonnet | sonnet | 0%（该用就得用） |
| 混合工作流 | 100% sonnet | 50% haiku + 50% sonnet | **~60%** |

## 🔄 APPLICATION — Hermes 集成方案

### 已落地 ✅
- **cc 已安装** — `D:\Reasonix\.claude\hooks\model-router.py`
- **hook 已注册** — `.claude/settings.json`
- **规则适配** — 中文关键词 + 消息长度 + 任务类型

### Hermes 自身的路由

Hermes 已配置 fallback（pro → flash），这是"被动切换"。主动路由需要 Hermes 支持类似 hook 机制。当前替代方案：
- 下次会话用 `hermes -c` 启动（默认 pro）
- 我（指挥官）在拆解任务时手动指定：简单子任务派给 flash，复杂任务派给 pro

### 效果验证
```bash
# 查看路由是否生效 — 看 cc 执行任务时实际用的模型
# 复杂任务应该看到 sonnet，简单任务应该看到 haiku
```

**关联技能：** [[ai-commander-system]], [[harness-engineering]], [[hermes-config]]
**改造路径：** 创建 `hermes-model-router` skill，封装路由规则，指挥官在拆解任务时自动套用
**预期效果：** cc 的 token 成本降低 50-60%，简单查询不再浪费 sonnet

## 📊 飞轮日志
- 本轮从 0xrdan/claude-router 学到了 hook 路由模式
- 已落地到 cc（Claude Code）执行层
- Hermes 侧的主动路由待 Hermes 本身支持 hook
