---
id: 20260529-metagpt
title: MetaGPT 多Agent协作框架拆解
tags: [skill-learning, automation, agent-upgrade, team-collaboration]
source_url: https://github.com/geekan/MetaGPT
date_created: 2026-05-29
last_updated: 2026-05-29
---

## 🎯 核心痛点与应用场景

单Agent处理复杂软件工程任务时，上下文窗口有限、推理链过长、输出质量不稳定。MetaGPT 将软件工程的标准作业流程 (SOP) 编码为多Agent协作网络，模拟产品经理、架构师、工程师等角色的真实协作。典型场景包括：从一句话需求自动生成完整项目代码、自动化 PRD 撰写与评审、端到端软件开发流水线。

## 🛠️ 底层原理解析

MetaGPT 的核心架构由三个支柱构成：

1. **SOP 驱动协作**：将软件开发流程（需求分析→系统设计→编码→测试）固化为 Agent 之间的有向消息传递链。每个 Agent 持有特定领域知识，按 SOP 顺序激活。

2. **共享环境 (Environment)**：基于发布/订阅模式的消息总线。所有 Agent 共享同一个 Environment 实例，通过 `env.publish_message(msg)` 广播结构化输出，其他角色通过 observe 机制拉取消息。

3. **结构化输出**：每个 Agent 的输出被约束为 JSON Schema，确保生成内容可解析、可验证。例如架构师输出系统设计文档、工程师输出符合接口约定的代码。

**核心执行循环**：`Role._observe()` → `_think()` → `_act()` → `env.publish_message(msg)`

- `_observe()`：从 Environment 拉取消息，筛选自身关心的信息（PM 关注需求变更，Engineer 关注设计文档）。
- `_think()`：基于观察到的消息和自身角色设定进行推理，决定下一步行动。
- `_act()`：执行行动（调用 LLM 生成结构化文档、代码等）。
- `env.publish_message(msg)`：将产出物发布回总线，供下游 Agent 消费。

这一设计使整个开发流程可追溯、可审计，每一步输出都是带 Schema 约束的文档。

## 🔄 Hermes 进化映射 (Integration Roadmap)

MetaGPT 的 SOP 多Agent模式为 Hermes 提供了清晰的进化方向：

| 应用场景 | MetaGPT 对应能力 | Hermes 实现路径 |
|----------|-----------------|----------------|
| 需求→代码自动生成 | PM + Architect + Engineer SOP 链 | 新增 [[SOP驱动开发]] Skill，定义需求解析→方案设计→代码输出的 Agent 流水线 |
| 结构化工件生成 | 基于 JSON Schema 的约束输出 | 扩展 [[Agent协作模式]]，引入 Schema 验证中间件，确保 Skill 输出可被下游解析 |
| 多角色任务编排 | Environment 发布/订阅消息总线 | 实现消息路由机制，让多个 Skill/Plugin 通过共享消息总线按序协作 |

> 核心启示：SOP 不是约束，而是放大。将领域知识编码为 Agent 协作流水线，能让单次推理无法完成的复杂任务被拆解为多个专注的子任务，由不同角色有序完成。

**相关链接**：[[Agent协作模式]] [[SOP驱动开发]]

---

*Stars: ~53K | Language: Python | Author: @geekan*
