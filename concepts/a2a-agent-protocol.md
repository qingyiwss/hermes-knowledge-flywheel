---
id: 20260529-a2a
tags: [skill-learning, automation, agent-upgrade, team-collaboration]
created: 2026-05-29
---

# A2A Agent 通信协议

## 这是什么

Google A2A（Agent-to-Agent）是一个开源的 Agent 间通信协议（⭐15K），定义了不同 Agent 如何发现彼此、协商能力、派发任务并追踪执行过程。它让多个独立 Agent 能像团队成员一样协同工作，而不需要硬编码的调用关系。

核心由三个组件构成：

- **Agent Card**（能力声明）：每个 Agent 暴露一张 JSON 卡片，声明自己能做什么、支持什么输入输出格式、端点地址。其他 Agent 通过读取卡片来「认识」彼此。
- **Task**（结构化任务）：所有工作被建模为 Task 对象，包含唯一 ID、状态、输入/输出工件（Artifact）。不再用「调一下那个脚本」的模糊方式，而是发出一个可追踪的任务。
- **状态机**：Task 经历 `pending → working → completed`（或 `failed`、`cancelled`）的生命周期，每一步都可观测、可审计。支持流式推送状态变更（SSE），实现实时进度反馈。

## 为什么重要

对团队提升有三个直接影响：

1. **统一接口，替代 shell 命令派发**：以前 Agent A 调用 Agent B 可能靠 `subprocess.run("python task.py")`，脆弱且无反馈。A2A 用标准化 Task API 取代 ad-hoc 脚本调用，任何语言实现的 Agent 都能互操作。
2. **任务生命周期可追踪**：每个 Task 有状态、有 ID、有超时、有错误信息。不再出现「那个任务跑哪去了？」的困惑——任何 Agent 都可以通过 Task ID 查询进度。
3. **共享记忆与上下文**：Task 的 Artifact 可在 Agent 间传递，形成链式工作流。前一个 Agent 的输出自动成为下一个 Agent 的输入，实现类似 [[记忆系统]] 的知识流转。

## 怎么用

基本流程：

1. **部署 Agent**：每个 Agent 在自己的进程中运行，暴露 A2A 兼容的 HTTP 端点（`/a2a` 或类似路径）。
2. **注册能力**：在 Agent Card 中声明 `skills` 列表，描述可处理的任务类型和参数 schema。
3. **发现与协商**：上游 Agent（如编排器）读取下游 Agent 的 Card，判断其是否能处理当前任务。
4. **派发任务**：通过 `POST /tasks/send`（或流式 `tasks/sendSubscribe`）发送 Task 对象。
5. **轮询或订阅**：下游 Agent 按状态机执行任务，上游可轮询 `GET /tasks/{id}` 或通过 SSE 订阅状态变更。
6. **获取结果**：当 Task 进入 `completed` 状态，从 Artifact 中提取输出。

与 [[多Agent协作]] 结合，A2A 可作为团队内部 Agent 的标准通信层，替代自定义 RPC 和消息队列的碎片化实现。

---

## 相关资源

- [Google A2A GitHub](https://github.com/google/A2A)
- A2A 规范草案：`a2a-specification` 仓库中的 `specification/` 目录
