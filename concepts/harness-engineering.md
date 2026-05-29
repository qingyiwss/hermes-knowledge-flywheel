---
id: 20260529-0001
title: Harness 工程 — Agent 产品的正确构建范式
tags: [skill-learning, agent-architecture, harness, claude-code]
source_url: https://github.com/shareAI-lab/learn-claude-code
date_created: 2026-05-29
confidence: high
---

# Harness 工程 — Agent 产品的正确构建范式

## 🎯 WHAT — 核心问题与原理

**问题：** 大多数"AI Agent 框架"其实是 Rube Goldberg 机器 — 用 if-else 和节点图把 LLM 调用串起来，以为这就是 Agent。

**核心论点：** Agency（自主行动能力）来自模型训练，不是来自外部代码编排。Agent 产品 = 模型（智能体）+ Harness（运行环境）。

**Harness 的五要素：**
```
Harness = Tools + Knowledge + Observation + Action + Permissions

    Tools:       file I/O, shell, network, database, browser
    Knowledge:   product docs, domain references, API specs, style guides
    Observation: git diff, error logs, browser state, sensor data
    Action:      CLI commands, API calls, UI interactions
    Permissions: sandbox isolation, approval workflows, trust boundaries
```

## 🛠️ HOW — 关键实现

Claude Code 的精简架构：
```
Claude Code = one agent loop
            + tools (bash, read, write, edit, glob, grep, browser...)
            + on-demand skill loading
            + context compaction
            + subagent spawning
            + task system with dependency graphs
            + async mailbox team coordination
            + worktree-isolated parallel execution
            + permission governance
```

**六个核心模式：**

1. **Agent Loop（不做状态机）** — 单一循环：接收输入 → 调用工具 → 观察结果 → 推理 → 下一步。没有 if-else 路由。

2. **On-Demand Skill Loading（按需加载）** — Skills 不是启动时全部加载，而是任务匹配时动态注入。省 token。

3. **Context Compaction（上下文压缩）** — 历史对话压缩到摘要，保留关键决策点。防止上下文溢出。

4. **Subagent Spawning（子代理隔离）** — 每个子任务用全新上下文，不污染主代理。delegate_task 就是这个模式。

5. **Task System with Dependencies（任务依赖图）** — 父任务完成才触发子任务。Kanban 的 parents=[] 就是这个。

6. **Worktree Isolation（工作区隔离）** — git worktree 让并行任务在独立文件系统空间运行，避免冲突。

## 🔄 APPLICATION — Hermes 集成方案

### 我们已对齐的部分 ✅
- ✅ Agent Loop = project-commander 的 6 步法
- ✅ Subagent = delegate_task 派发 cc
- ✅ On-Demand Skills = skill_view 按需加载
- ✅ Task Dependencies = todo 系统

### 可以改进的部分 ⚠️

**1. Harness 意识升级**
当前 project-commander 偏重"流程编排"。应该升级为"Harness 构建者"思维：
- 不只是发任务，而是给 cc 配好工具、知识、观察、权限
- 每次任务前检查：tool/task 配置是否足够？

**2. 上下文管理**
当前没有 context compaction 机制。长时间会话会有 token 膨胀。
→ 可加入定期摘要归档 + 清理

**3. 权限边界**
当前 cc 的 settings.json 有 allow/ask/deny 白名单，但不够细粒度。
→ 可参考 Claude Code 的 Bash(npm run lint:*) 模式，给工具添加参数级白名单

**关联技能：** [[ai-commander-system]], [[hermes-config]]
**改造路径：** 更新 `project-commander` 技能，加入 Harness 五要素检查表
**预期效果：** 每次派发任务前，自动验证工具/知识/权限是否就绪，减少执行失败率
