---
title: AI 指挥官系统架构
created: 2026-05-29
updated: 2026-05-29
type: concept
tags: [hermes, claude-code, reasonix, automation]
confidence: high
---

# AI 指挥官系统架构

## 架构图

```
用户（司令）
  ↓ 发指令 "帮我做XX"
Hermes Agent（指挥官 / project-commander）
  ↓ 拆解任务 + 并行派发 + 审核验收
┌─────────────┴─────────────┐
cc（Claude Code）     Reasonix（投资工具）
  写代码 / 重构         回测 / 定投 / 估值
```

## 各组件角色

### Hermes Agent（指挥官模式）
- **技能**：`project-commander`
- **职责**：接收用户指令 → 拆解 → 派发子代理 → 三关审核（规格/质量/回归）→ 汇报
- **主模型**：deepseek-v4-pro
- **Fallback**：deepseek-v4-flash

### Claude Code（执行层）
- **技能**：`claude-code`
- **职责**：按指挥官派发的任务写代码、重构、分析
- **工作目录**：`D:\Reasonix\`
- **配置**：`CLAUDE.md` + `.claude/rules/` + `.claude/settings.json`
- **模式**：优先用 print mode（`claude -p`），复杂交互用 tmux

### Reasonix（专用工具）
- **技能**：`reasonix`
- **位置**：`D:\Reasonix\`
- **核心**：估值择时定投、10年回测
- **桌面应用**：`reasonix-desktop.exe`

## 工作流

```
1. 用户 "加一个中证红利回测"
2. 指挥官拆解：修改 backtest_10y.js → 跑回测 → 验证结果
3. 派 cc：cd /d/Reasonix && claude -p "add 中证红利 strategy"
4. 指挥官审核：跑 node backtest_10y.js --json，对比预期
5. 汇报："完成了，回测结果如下"
```

- **扩展方向**
- [[hermes-config]] — Hermes 模型和配置
