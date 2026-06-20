---
id: 20260531-autogen
title: Microsoft AutoGen 多Agent框架拆解 — 对话模式、工具调用、代码沙箱、多Agent编排
tags: [hermes, agent-upgrade, multi-agent, workflow, communication, cc, sandbox, tool-calling]
source_url: https://github.com/microsoft/autogen
date_created: 2026-05-31
updated: 2026-05-31
last_updated: 2026-05-31
confidence: high
---

# Microsoft AutoGen 多Agent框架拆解

> ⭐ 58,553 | MIT License | Python 3.10+ / .NET 双语言 | 已进入维护模式，后继者 [Microsoft Agent Framework (MAF)](https://github.com/microsoft/agent-framework)

> **⚠️ 关键提醒**：AutoGen 已于 2025 年进入 maintenance mode，不再接收新功能。新项目应从 MAF 起步。但 AutoGen 的架构设计（分层+事件驱动+发布订阅）仍是理解多Agent系统的绝佳样本。

---

## 🎯 WHAT — 核心问题与原理

### 它解决什么？

AutoGen 让开发者构建**能自主行动或与人类协作的多Agent AI应用**。核心挑战是：

1. **Agent 如何对话？** 多个 LLM Agent 如何进行结构化、有上下文的对话，而不是各自为政？
2. **Agent 如何用工具？** Agent 需要调用外部工具（API、代码执行、MCP Server），但 LLM 的 function calling 格式混乱、易失败。
3. **代码如何安全执行？** Agent 生成的代码不能直接在生产环境运行——需要隔离沙箱。
4. **多Agent如何编排？** 多个专业Agent（数学专家、化学专家、编码专家）如何按需调度？
5. **人类何时介入？** 关键操作需要人类审批——但不是每个步骤都打断。

### AutoGen 的核心理念：分层架构 + 发布订阅消息总线

```
┌────────────────────────────────────────────┐
│              AgentChat API                  │
│  (高级API：AssistantAgent, Team, Handoff)    │
├────────────────────────────────────────────┤
│              Core API                       │
│  (消息传递、事件驱动Agent、本地/分布式运行时) │
├──────────────┬─────────────────────────────┤
│  Extensions  │         Developer Tools      │
│  (LLM客户端、 │    (AutoGen Studio, Bench)   │
│   代码执行)   │                              │
└──────────────┴─────────────────────────────┘
```

三层设计：Core 做消息总线，AgentChat 做高层封装，Extensions 做能力扩展。

### 四大核心能力

| 能力 | AutoGen 实现 | 关键设计 |
|------|-------------|---------|
| **Agent 对话** | `BaseChatAgent` + `on_messages()` 模式，每个Agent维护自己的状态，外部只传新消息 | 增量状态管理，不全量传历史 |
| **工具调用** | `BaseTool<T,R>` + `Workbench` + `FunctionTool`，支持 MCP Server 集成 | 统一的 Tool 协议+Workbench 抽象 |
| **代码执行沙箱** | `CodeExecutorAgent` + `DockerCommandLineCodeExecutor`，代码在 Docker 容器中执行 | 隔离执行 + 审批函数（Human-in-the-loop） |
| **多Agent编排** | `SelectorGroupChat`（LLM选下一发言人）/ `RoundRobinGroupChat`（轮询）/ `AgentTool`（嵌套Agent作工具） | 发布订阅消息总线，每个Agent有独立 topic |

---

## 🔧 HOW — 架构解构与实现细节

### 1. Agent 对话模式：增量状态 + 发布订阅

AutoGen 的 Agent 对话基于 Core API 的**消息传递系统**：

```python
# Core Agent Protocol（最底层）
class Agent(Protocol):
    @property
    def id(self) -> AgentId: ...
    @property
    def metadata(self) -> AgentMetadata: ...
    async def on_message(self, message: Any, ctx: MessageContext) -> Any: ...
    async def save_state(self) -> Mapping[str, Any]: ...
    async def load_state(self, state: Mapping[str, Any]) -> None: ...
```

**关键设计决策**：
- **增量消息**：Agent 维护内部状态（`_model_context`），调用者**每次只传新消息**，不传全部历史。这避免了上下文膨胀和状态同步问题。
- **发布订阅**：Core Runtime 使用 `AgentRuntime` + `TypeSubscription` 实现主题（topic）发布订阅。每个 Agent 订阅特定 topic，运行时自动路由消息。
- **AgentContainer**：GroupChat 中的每个参与者被包装在 `ChatAgentContainer` 中，负责将 `BaseChatMessage` 转换为 Core 消息并发布到 group topic。

**消息类型体系**：

```
BaseMessage
├── BaseChatMessage（Agent间通信）
│   ├── TextMessage（纯文本）
│   ├── StructuredMessage（结构化Pydantic）
│   ├── HandoffMessage（Agent切换）
│   ├── StopMessage（终止信号）
│   └── ToolCallSummaryMessage（工具调用摘要）
└── BaseAgentEvent（可观测事件，给UI/用户）
    ├── ThoughtEvent（思考过程）
    ├── ToolCallRequestEvent（工具调用请求）
    ├── ToolCallExecutionEvent（工具调用结果）
    ├── ModelClientStreamingChunkEvent（流式chunk）
    └── SelectorEvent（发言人选秀）
```

**对比 Hermes↔CC 通信**：
- Hermes 当前用 **终端 subprocess + 文本解析** 调用 Claude Code（`claude --print "task"`），每次调用返回完整文本输出，**无结构化消息、无状态管理、无流式事件**。
- AutoGen 用 **类型化消息 + 发布订阅**，每条消息有 `source`/`id`/`created_at`，可追踪、可审计、可流式。

### 2. 工具调用：统一 Tool 协议 + Workbench 抽象

```python
# Core Tool Protocol
class Tool(Protocol):
    name: str
    description: str
    schema: ToolSchema        # JSON Schema for LLM function calling
    def args_type() -> Type[BaseModel]: ...
    def return_type() -> Type[Any]: ...
    async def run_json(args: Mapping[str, Any], cancellation_token: CancellationToken) -> Any: ...

# Workbench — 工具集合的运行时容器
class Workbench(Protocol):
    async def call_tool(name: str, arguments: str, cancellation_token: CancellationToken) -> ToolResult: ...
    async def list_tools() -> List[ToolSchema]: ...
```

**关键设计**：
- `FunctionTool` 将任意 Python 函数包装为符合 `Tool` 协议的工具，自动从类型注解生成 JSON Schema。
- `Workbench` 抽象允许多种后端：`StaticStreamWorkbench`（本地工具）、`McpWorkbench`（MCP Server 工具）。
- `AgentTool` 允许将一个 **Agent 包装为另一个 Agent 的工具**——这是多Agent编排的基础能力。

**AssistantAgent 的工具循环**：
```python
# 伪代码：AssistantAgent 内部循环
async def on_messages(self, messages, cancellation_token):
    # 1. 模型推理 → 可能产生 tool_calls
    result = await model_client.create(messages_with_system_prompt)
    # 2. 如果有 tool_call，执行工具并收集结果
    for tool_call in result.content:
        tool_result = await workbench.call_tool(tool_call.name, tool_call.arguments)
        # 3. 将结果反馈给模型，让模型反思
        # 4. 重复直到 max_tool_iterations 或无 tool_call
    # 5. 返回最终文本响应
```

**对比 NΞXUS 当前工具调用**：
- Hermes 通过 `hermes_toolkit` 管理工具，每次 CC 返回后解析工具调用。
- AutoGen 的 Workbench 抽象更清晰：工具注册、执行、结果返回都在一个统一接口内完成。

### 3. 代码执行沙箱：Docker 隔离 + 审批函数

```python
class CodeExecutorAgent(BaseChatAgent):
    """生成并执行代码的 Agent"""
    def __init__(self, name, code_executor, model_client=None, 
                 approval_func=None, sources=None):
        # code_executor: DockerCommandLineCodeExecutor 或本地执行器
        # approval_func: 每次执行前调用的审批函数（Human-in-the-loop）
        # sources: 只处理来自特定 Agent 的代码块（安全过滤）

# 审批函数 — Human-in-the-loop 的关键
def approval_func(request: ApprovalRequest) -> ApprovalResponse:
    # request.code: 要执行的代码
    # request.context: 当前对话上下文
    # 返回 ApprovalResponse(approved=True/False, reason="...")
```

**执行流程**：
1. 接收包含代码块的消息（markdown code block）
2. 调用 `approval_func` 获取人类审批
3. 通过 `DockerCommandLineCodeExecutor` 在隔离容器中执行
4. 捕获 stdout/stderr + 退出码
5. （可选）模型反思执行结果，生成重试或最终响应

**安全层次**：
- Docker 容器隔离（文件系统、网络、进程）
- `sources` 过滤（只执行可信 Agent 的代码）
- `approval_func` 审批门（可选的人类审批）
- 超时控制 + 重试机制

### 4. 多Agent编排：Selector + RoundRobin + AgentTool

AutoGen 提供了 **3 种编排模式**：

#### a) SelectorGroupChat — LLM 驱动的发言人选秀

```python
class SelectorGroupChat(BaseGroupChat):
    """由 LLM 模型选择下一个发言人的群聊"""
    # 使用 selector_prompt 指导模型选择发言人
    # 支持自定义 selector_func 和 candidate_func
    # allow_repeated_speaker 控制是否允许连续发言
```

**核心机制**：SelectorGroupChatManager 维护一个 `model_context`，每次需要选择下一个发言人时，将所有参与者的 description 和当前对话线程发给 LLM，LLM 选择最合适的发言人。这是 **「Agent 自觉」模式——Agent 自己决定谁该说话**。

#### b) RoundRobinGroupChat — 轮询式发言

```python
class RoundRobinGroupChat(BaseGroupChat):
    """按固定顺序轮流发言的群聊"""
    # _next_speaker_index 递增 % len(participants)
```

最简单但最可靠的编排模式，适合**已知流程**的多Agent协作。

#### c) AgentTool — Agent 即工具

```python
math_agent_tool = AgentTool(math_agent, return_value_as_last_message=True)
chemistry_agent_tool = AgentTool(chemistry_agent, return_value_as_last_message=True)

orchestrator = AssistantAgent("orchestrator", tools=[math_agent_tool, chemistry_agent_tool])
```

**编排Agent 将子Agent 当作工具调用**——当用户问数学问题时，编排Agent 调用 `math_agent_tool`，子Agent 自主完成推理后返回结果。这是 **「Agent as Tool」模式**。

#### d) Handoff — Agent 直接移交

```python
class Handoff(BaseModel):
    target: str       # 目标 Agent 名称
    description: str  # 何时应该 handoff
    message: str      # 移交给目标 Agent 的消息
    
    @property
    def handoff_tool(self) -> BaseTool:
        # 将 handoff 包装为工具，Agent 可主动调用
```

Handoff 允许 Agent **主动将控制权移交给另一个 Agent**，并附带上文。GroupChat 中，Handoff 消息触发发言人选秀，让目标 Agent 获得发言权。

### 5. 终止条件：可组合的状态机

```python
# 终止条件可组合
cond = MaxMessageTermination(10) | TextMentionTermination("TERMINATE")
cond = MaxMessageTermination(10) & TextMentionTermination("TERMINATE")

# 条件组合：AND/OR
# 条件重置：reset()
```

### 6. 运行时架构：SingleThreadedAgentRuntime

```python
class SingleThreadedAgentRuntime:
    """单线程 Agent 运行时，基于发布订阅"""
    # 内置 topic 系统：每个 Agent 注册到特定 topic
    # Agent 间通过 publish_message() + topic 通信
    # 支持嵌入式使用（不依赖外部消息队列）
```

---

## 🔗 APPLICATION — 与 NΞXUS 融合应用

### A2A vs AutoGen vs NΞXUS 三角对比

| 维度 | Google A2A | Microsoft AutoGen | NΞXUS 当前 |
|------|-----------|-------------------|-----------|
| **通信协议** | HTTP REST + SSE | 发布订阅 Topic（内存/分布式） | subprocess 文本 |
| **Agent 发现** | Agent Card（JSON声明） | Agent 注册到 Runtime | 硬编码调用 |
| **任务建模** | Task（状态机+Artifact+ID） | BaseChatMessage（有ID但不追踪） | 无结构化任务 |
| **消息类型** | 无强类型（JSON自由格式） | Pydantic类型化消息 | 纯文本 |
| **编排模式** | 被动（Agent等待任务） | 主动（Selector+RoundRobin+AgentTool） | 主从式（Hermes 调度 CC） |
| **代码执行** | ❌ 不在协议层 | ✅ Docker 沙箱+审批 | 终端直接执行 |
| **流式支持** | ✅ SSE | ✅ AsyncGenerator | ❌ |
| **跨语言** | HTTP 天然跨语言 | Python/.NET 双语言 SDK | subprocess 天然跨语言 |

### 借鉴 AutoGen 升级 NΞXUS Hermes↔CC 通信

当前 Hermes↔CC 通信的核心痛点是**无结构化、无状态追踪、无流式反馈**。AutoGen 提供了一套可直接借鉴的模式：

#### 方案一：引入消息总线（短中期）

```
当前：
  Hermes ──subprocess("claude --print 'task'")──► CC
              ◄── 纯文本响应 ──

升级后：
  Hermes ──publish(TaskRequestMessage, topic="cc")──► Topic Bus
              ◄── subscribe(topic="hermes") ──── CC 的响应消息流
```

**落地步骤**：
1. 定义 **Pydantic 消息类型** 替代文本：
   - `TaskRequestMessage(source, task_id, instruction, context)`
   - `ToolCallRequestMessage(source, tool_name, arguments)`
   - `ToolResultMessage(source, task_id, result)`
   - `ThoughtEvent(source, reasoning)` — 思考流
   - `StreamChunkEvent(source, text_chunk)` — 流式输出

2. 使用 **asyncio.Queue + topic 系统**（借鉴 `SingleThreadedAgentRuntime`）：
   - Hermes 向 `topic="cc_executor"` 发布任务
   - CC 向 `topic="hermes_listener"` 发布响应
   - 工具执行器向 `topic="tool_results"` 发布执行结果

3. CC 侧改动最小：通过 `--print` 输出结构化 JSON（每行一个消息类型），Hermes 侧解析后转为 Pydantic 对象。

#### 方案二：借鉴 AutoGen 的 SelectorGroupChat 实现智能调度

```
NΞXUS 多Agent架构（借鉴 SelectorGroupChat）：

┌───────────────────────────────────────────────┐
│            NΞXUS Orchestrator                  │
│           (Selector 模式)                       │
│  ┌─────────┐  ┌─────────┐  ┌───────────────┐  │
│  │ Hermes  │  │   CC    │  │ 代码执行沙箱   │  │
│  │(分析推理)│  │(代码修改)│  │ (Docker隔离)  │  │
│  └─────────┘  └─────────┘  └───────────────┘  │
│  ┌─────────┐  ┌─────────────────────────────┐  │
│  │ 文件系统│  │  Human-in-the-loop (审批)    │  │
│  │  工具   │  │                               │  │
│  └─────────┘  └─────────────────────────────┘  │
└───────────────────────────────────────────────┘
```

**Selector Prompt 示例**：
```
你是一个 NΞXUS 编排器。根据当前对话和任务，选择最合适的 Agent 下一步发言：

可用 Agent：
- hermes: 深度分析、推理、工具调用编排
- cc: 代码修改、文件操作、git 操作
- sandbox: 安全代码执行和验证
- human: 需要人类审批的关键操作

当前任务：{task_description}
对话历史：{history}

下一个发言人应该是谁？只输出 Agent 名称。
```

#### 方案三：Handoff 模式实现 Hermes↔CC 无缝切换

```python
# 借鉴 AutoGen Handoff 设计
class NEXUSHandoff(BaseModel):
    target: str          # "cc" 或 "hermes"
    message: str         # 上下文消息
    context: List[LLMMessage]  # 完整对话历史

# Hermes 说"这部分需要 CC 修改代码"时：
handoff = Handoff(target="cc", message="请修改 src/tools.py 的第42-58行")
# CC 完成后：
handoff = Handoff(target="hermes", message="修改完成，diff 如下：...")
```

#### 方案四：AutoGen CodeExecutorAgent 升级为 NΞXUS 代码执行沙箱

借鉴 `CodeExecutorAgent` + `approval_func` 设计：
- **所有 CC 的代码修改在验证沙箱中先行测试**
- **关键操作（文件删除、git push、pip install）触发审批**
- **执行结果结构化返回（stdout + stderr + exit_code + 耗时）**

### 与 A2A 的互补性

| 借鉴方向 | 推荐来源 | 原因 |
|---------|---------|------|
| Agent 对话模式 | **AutoGen** | SelectorGroupChat + AgentTool + Handoff 提供了 A2A 没有的主动编排模式 |
| 任务追踪 + 状态机 | **A2A** | Task ID + 状态机比 AutoGen 的消息模型更适合审计 |
| 跨语言互操作 | **A2A** | HTTP + JSON 比发布订阅更适合多语言环境 |
| 消息类型系统 | **AutoGen** | Pydantic 类型化消息比 A2A 的自由 JSON 更安全 |
| 代码沙箱 | **AutoGen** | DockerCodeExecutor 是现成的安全执行方案 |

**推荐融合方案**：A2A 的 Task 生命周期 + AutoGen 的 SelectorGroupChat 编排 + AutoGen 的消息类型系统 + 自建代码沙箱。

---

## 📊 飞轮日志

| 字段 | 值 |
|------|-----|
| 轮次 | 第 N+1 轮 |
| 分析对象 | microsoft/autogen（⭐58,553） |
| 数据来源 | GitHub raw README + 9 个核心源文件（_assistant_agent.py / _base_group_chat.py / _selector_group_chat.py / _round_robin_group_chat.py / _code_executor_agent.py / messages.py / _agent.py / _handoff.py / _base.py tools） |
| 分析深度 | 源码级 |
| 关键发现 | 1) 分层架构（Core/AgentChat/Extensions）是应对复杂度关键；2) SelectorGroupChat 的 LLM 选发言人比 A2A 被动等待更适合主动式多Agent编排；3) 消息类型体系（BaseChatMessage vs BaseAgentEvent）优雅分离通信和可观测性；4) AgentTool 模式让 Agent 可被其他 Agent 当工具调用 |
| 落地建议 | 分 3 阶段：① 引入 Pydantic 消息类型替代文本通信；② 实现 asyncio Queue topic 总线；③ 上线 Selector 编排 + Handoff 切换 + 代码沙箱 |
| 风险提示 | AutoGen 已进入 maintenance mode。核心逻辑可借鉴，但新功能应参考 MAF（Microsoft Agent Framework）的 A2A 集成路径 |
