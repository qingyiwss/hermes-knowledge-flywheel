---
created: 2026-05-31
updated: 2026-05-31
title: "ACI — 开源多租户工具调用平台深度拆解"
category: "AI Infrastructure / Tool Calling Platform"
tags: ["tool-calling", "mcp", "function-calling", "agent", "oauth2", "multi-tenant", "vibeops", "integration-platform"]
stars: 4793
language: "Python (FastAPI)"
license: "Apache-2.0"
---

# ACI — 开源多租户工具调用平台深度拆解

> 仓库：[aipotheosis-labs/aci](https://github.com/aipotheosis-labs/aci) · ⭐ 4,793 · 🍴 462 · License: Apache-2.0
> 官网：[aci.dev](https://www.aci.dev/) · 定位：_The birthplace of VibeOps_

---

## 1. 项目概要

ACI（Agent-Centric Integration）是由 aipotheosis-labs 开源的**工具调用平台**，核心理念是：**让 AI Agent 以统一、安全、可审计的方式访问 600+ 第三方服务**。

它不仅是一个"工具集"，更是一套完整的**工具生命周期管理基础设施**——从工具的声明式注册、多租户认证、细粒度权限控制、自然语言意图发现，到最终的执行与审计日志，形成了一条完整的闭环。

### 核心能力一览

| 维度 | 能力 |
|------|------|
| **接入方式** | ① 直接 Function Calling（Python/TypeScript SDK） ② **统一 MCP Server**（Unified MCP） |
| **集成规模** | 600+ 预构建集成（Brave Search、Gmail、Slack、GitHub、Notion、Supabase、Vercel、Cloudflare 等） |
| **认证体系** | API Key / OAuth2 / No Auth，支持多租户，自动 Token 刷新 |
| **权限模型** | Project → Agent → App Configuration → Function → Linked Account 五级粒度 |
| **工具发现** | 基于向量嵌入（pgvector）的语义搜索，按自然语言意图匹配工具 |
| **安全护栏** | 可见性过滤（visible/invisible 参数）、自然语言权限边界（NL Custom Instructions）、速率限制、配额管理 |
| **框架无关** | 输出 OpenAI / Anthropic / Basic 三种 Function Definition 格式 |
| **部署形态** | 开源自托管（FastAPI + PostgreSQL）或托管服务（aci.dev） |

---

## 2. 核心架构：从注册到执行的全链路

### 2.1 整体请求生命周期

```
┌──────────────┐     API Key      ┌─────────────────────────────────────────────┐
│  AI Agent    │ ───────────────> │              ACI Backend (FastAPI)           │
│  (IDE/SDK)   │                  │                                              │
└──────────────┘                  │  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
                                  │  │ RateLimit│→ │API Key   │→ │Project     │ │
                                  │  │Middleware│  │Validation│  │Quota Check │ │
                                  │  └──────────┘  └──────────┘  └────────────┘ │
                                  │                     ↓                        │
                                  │  ┌──────────────────────────────────────┐   │
                                  │  │         execute_function()            │   │
                                  │  │  ① Function Lookup (DB)               │   │
                                  │  │  ② App Config Check (enabled?)        │   │
                                  │  │  ③ Agent Allowed Apps Check           │   │
                                  │  │  ④ Function Enabled Check             │   │
                                  │  │  ⑤ Linked Account Check               │   │
                                  │  │  ⑥ Fetch Security Credentials         │   │
                                  │  │  ⑦ Custom Instructions Violation Check│   │
                                  │  │  ⑧ Dispatch Executor                  │   │
                                  │  └──────────────────────────────────────┘   │
                                  │                     ↓                        │
                                  │  ┌──────────────────────────────────────┐   │
                                  │  │  Function Executors (Strategy Pattern)│   │
                                  │  │  ├─ RestAPIKeyFunctionExecutor        │   │
                                  │  │  ├─ RestOAuth2FunctionExecutor        │   │
                                  │  │  ├─ RestNoAuthFunctionExecutor        │   │
                                  │  │  └─ ConnectorFunctionExecutor         │   │
                                  │  └──────────────────────────────────────┘   │
                                  └─────────────────────────────────────────────┘
```

### 2.2 工具注册：声明式 JSON 定义

ACI 的工具注册采用**纯声明式 JSON 文件**方式，每个集成包含两个核心文件：

#### `app.json` — 应用元数据与认证

```json
{
  "name": "BRAVE_SEARCH",
  "display_name": "Brave Search",
  "provider": "Brave Software, Inc.",
  "security_schemes": {
    "api_key": {
      "location": "header",
      "name": "X-Subscription-Token",
      "prefix": null
    }
  },
  "categories": ["Search & Scraping"],
  "visibility": "public"
}
```

#### `functions.json` — 函数/工具定义

```json
{
  "name": "BRAVE_SEARCH__WEB_SEARCH",
  "description": "Brave Web Search API...",
  "protocol": "rest",
  "protocol_data": {
    "method": "GET",
    "path": "/web/search",
    "server_url": "https://api.search.brave.com/res/v1"
  },
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "object",
        "properties": { "q": { "type": "string" }, "country": { "type": "string", "default": "US" } },
        "required": ["q"],
        "visible": ["q", "country"]
      },
      "header": {
        "type": "object",
        "properties": { "Accept": { "type": "string", "default": "application/json" } },
        "required": [],
        "visible": []
      }
    },
    "required": ["query", "header"],
    "visible": ["query"]
  }
}
```

**关键设计洞察**：`visible` 字段是 ACI 最精妙的设计之一。它允许定义者将参数分为两类：
- **Visible**：暴露给 LLM，Agent 可以理解和填充
- **Invisible**：对 LLM 隐藏，由系统自动注入（如认证头、默认值、内部字段）

这解决了 LLM 工具调用中的一个核心矛盾——既要给 Agent 足够的上下文来正确调用工具，又要防止 context window 被无关细节撑爆。

### 2.3 工具调用：多级安全检查链

ACI 的 `execute_function()` 实现了**7 层递进式安全检查**：

```python
# 第1层: 函数是否存在
function = crud.functions.get_function(...)

# 第2层: App 是否已配置
app_configuration = crud.app_configurations.get_app_configuration(...)

# 第3层: App 配置是否启用
if not app_configuration.enabled: raise AppConfigurationDisabled(...)

# 第4层: Agent 是否有权使用此 App
if function.app.name not in agent.allowed_apps: raise AppNotAllowedForThisAgent(...)

# 第5层: 该函数是否在 App 配置中启用
if not app_configuration.all_functions_enabled and function.name not in app_configuration.enabled_functions:
    raise FunctionNotEnabledInAppConfiguration(...)

# 第6层: Linked Account 是否存在且启用
linked_account = crud.linked_accounts.get_linked_account(...)
if not linked_account or not linked_account.enabled: raise ...

# 第7层: 自然语言权限边界检查
custom_instructions.check_for_violation(openai_client, function, function_input, agent.custom_instructions)
```

### 2.4 安全凭证管理：三种认证模式

ACI 实现了三种认证模式的统一抽象：

| 模式 | 凭证来源 | 凭证刷新 | 默认凭证 |
|------|---------|---------|---------|
| **API Key** | Linked Account 或 App 默认共享 Key | 无需刷新 | 支持（fallback 到 App 级别） |
| **OAuth2** | 用户 OAuth 授权后的 Access Token | 自动刷新（expires_at 检查 + refresh_token） | 不支持（OAuth2 必须 per-user） |
| **No Auth** | 无 | — | — |

OAuth2 Token 管理特别值得关注——ACI 在每次函数执行前检查 `expires_at`，过期则自动使用 `refresh_token` 刷新，并将新 token 写回数据库。这确保了长期运行的 Agent 不会因 token 过期而中断。

### 2.5 函数执行器：策略模式

```python
def get_executor(protocol: Protocol, linked_account: LinkedAccount) -> FunctionExecutor:
    match protocol, linked_account.security_scheme:
        case Protocol.REST, SecurityScheme.API_KEY:
            return RestAPIKeyFunctionExecutor(linked_account)
        case Protocol.REST, SecurityScheme.OAUTH2:
            return RestOAuth2FunctionExecutor(linked_account)
        case Protocol.REST, SecurityScheme.NO_AUTH:
            return RestNoAuthFunctionExecutor(linked_account)
        case Protocol.CONNECTOR, _:
            return ConnectorFunctionExecutor(linked_account)
```

- **REST 执行器**：构建 HTTP 请求（httpx），自动注入凭证到 header/query/body/cookie，支持 form-encoded 和 JSON body
- **Connector 执行器**：动态导入本地 Python 模块（`aci.server.app_connectors.{app_name}`），调用对应类的方法。适用于需要 SDK 封装或复杂业务逻辑的场景（如 Gmail、Vercel、E2B 等）

### 2.6 工具发现：向量语义搜索

ACI 的工具发现不走传统的"列出所有工具"路线，而是：

1. **离线**：为每个 Function 生成 OpenAI Embedding（name + description + parameters），存入 pgvector
2. **在线**：Agent 传入自然语言 `intent`（如 "我想搜索网页"），系统生成 intent embedding，用 `cosine_distance` 排序返回最匹配的工具
3. **过滤**：同时支持按 App 名称过滤、仅返回 Agent 已启用工具的 `allowed_only` 模式

这解决了 **600+ 工具不可能全部塞进 LLM Context Window** 的问题——Agent 只需描述意图，系统自动发现最相关的工具。

### 2.7 自然语言权限边界（Custom Instructions）

这是 ACI 最具创新性的安全机制之一：

- 每个 Agent 可以配置 `custom_instructions`（`dict[function_name, instruction]`）
- 在函数执行前，系统调用 `gpt-4o-mini` 判断此次调用是否违反自然语言指令
- 例如：`"GMAIL__SEND_EMAIL": "只允许发送给 @company.com 域名的收件人"`
- 如果 LLM 判断违规，抛出 `CustomInstructionViolation`，阻止执行

**与传统 RBAC 的对比**：RBAC 只能做二进制的"允许/拒绝"，而自然语言边界可以做语义级别的约束，如"不允许发送超过 100 字的邮件"或"只允许查询最近 7 天的数据"。

---

## 3. 与 MCP（Model Context Protocol）的对比

ACI 与 Anthropic 的 MCP 是当前工具调用领域两大主流方案。它们解决相同的问题（让 AI Agent 访问外部工具），但架构哲学截然不同。

### 3.1 架构对比表

| 维度 | **ACI** | **MCP (Anthropic)** |
|------|---------|---------------------|
| **核心理念** | 中心化工具网关 | 去中心化工具协议 |
| **工具托管** | 云端平台统一托管 600+ 工具 | 每个工具独立部署为 MCP Server |
| **发现机制** | 向量语义搜索 + 过滤 | 客户端直连 Server，列出所有工具 |
| **认证模型** | 多租户 OAuth2/API Key，平台代管 | 每个 MCP Server 自行处理认证 |
| **安全模型** | 7 层递进式检查 + NL 权限边界 | 依赖 MCP Server 自身实现 |
| **协议层** | REST API + MCP 适配层 | JSON-RPC over stdio/SSE |
| **工具定义** | 声明式 JSON（app.json + functions.json） | 代码内注册（`server.tool()` 装饰器） |
| **Context Window** | 意图搜索 → 按需返回相关工具 | 返回所有注册工具 |
| **框架兼容** | 输出 OpenAI/Anthropic/Basic 三种格式 | MCP 客户端协议（需适配） |
| **部署复杂度** | 开源自托管或托管服务 | 每个工具需独立部署进程 |
| **适合场景** | 多 Agent、多用户、需要统一管理的企业场景 | 单 Agent、工具较少、需要极简部署的个人场景 |

### 3.2 关键差异深度解析

#### 3.2.1 工具发现：搜索 vs 枚举

MCP 的 `tools/list` 方法返回 Server 上所有工具的定义。当工具数量增长到几十个以上时，这会迅速撑爆 LLM Context Window（例如 600 个工具的定义轻松超过 100K tokens）。

ACI 的方案更聪明：Agent 传 `intent` 做语义搜索，系统只返回最相关的 N 个工具。这是一种**意图驱动的动态工具发现**，从根本上解决了大规模工具集的 context 管理问题。

#### 3.2.2 认证：代管 vs 自理

MCP 将认证完全下放给每个 MCP Server 实现者。如果你要接入 10 个 API，需要为每个配置不同的 API Key / OAuth 流程。ACI 则将认证集中管理——用户只需在 Dev Portal 中一次配置，所有 Agent 共享同一套认证基础设施，且 OAuth2 Token 自动刷新。

#### 3.2.3 安全：多层 vs 单层

MCP 的安全模型是"信任 MCP Server"——如果 Server 说某操作可以执行，Client 就执行。ACI 则在平台层实现了多层安全检查（Agent 白名单、App 配置状态、Function 启用状态、Linked Account 状态、NL 权限边界），即使工具定义本身没有问题，平台也可以阻止不合规的调用。

#### 3.2.4 ACI 的 MCP 定位：桥接而非替代

ACI 不是要替代 MCP，而是**在 MCP 之上提供一层统一网关**。ACI 的 `aci-mcp` 包提供了两种 MCP Server：
- **Apps Server**：将指定 App 的工具直接暴露为 MCP tools
- **Unified Server**：暴露两个元工具（`ACI_SEARCH_FUNCTIONS` + `ACI_EXECUTE_FUNCTION`），让 Agent 通过 MCP 协议间接访问 ACI 的全部 600+ 工具

这使得 ACI 可以融入任何支持 MCP 的生态（Claude Desktop、Cursor、Windsurf 等），同时保留其集中管理的优势。

### 3.3 融合趋势

ACI 和 MCP 正在走向互补：MCP 提供了标准化的 Client-Server 通信协议，而 ACI 提供了大规模工具管理的基础设施。未来理想的工具调用架构可能是：**用 MCP 协议通信，用 ACI 平台管理**。

---

## 4. Hermes 如何借鉴 ACI 的工具链设计

Hermes Agent 作为 Nous Research 的智能助手，可以从 ACI 的架构中汲取以下设计经验：

### 4.1 优先级一：声明式工具注册（可直接采纳）

ACI 的 `app.json` + `functions.json` 模式非常轻量且易于扩展。Hermes 可以参考此模式，将工具定义为：

```yaml
# hermes_tool.yaml
name: "web_search"
description: "Search the web"
protocol: "rest"
endpoint: "https://api.search.example.com/v1/search"
parameters:
  type: "object"
  properties:
    query:
      type: "string"
      description: "Search query"
  required: ["query"]
  visible: ["query"]  # Hermes 可借鉴：控制哪些参数暴露给 LLM
auth:
  type: "api_key"
  location: "header"
  name: "X-API-Key"
```

**收益**：工具的添加不再需要写代码，只需一个 YAML/JSON 文件。对于 Hermes 的插件生态，这意味着社区贡献工具的门槛大幅降低。

### 4.2 优先级一：visible/invisible 参数分离

ACI 的 `visible` 字段设计可以直接移植到 Hermes 的 tool schema 中：

- **Visible 参数**：暴露给 LLM，Agent 根据自己的判断填充
- **Invisible 参数**：LLM 看不到，由系统在运行时自动注入（如认证凭证、默认值、内部路由信息）

这对于 Hermes 尤其有价值——当前 Hermes 的 tool definition 会全部发送给 LLM，当工具参数包含大量认证/配置细节时，不仅浪费 token，还可能混淆 LLM 的判断。

### 4.3 优先级二：多执行器策略模式

ACI 的 `get_executor(protocol, security_scheme)` 工厂函数可以启发 Hermes 的工具执行架构重构：

```python
# Hermes 可以借鉴的模式
def get_executor(tool: Tool, auth: AuthContext) -> ToolExecutor:
    match tool.protocol:
        case "rest": return RestExecutor(tool, auth)
        case "python": return PythonExecutor(tool, auth)
        case "shell": return ShellExecutor(tool, auth)
        case "grpc": return GrpcExecutor(tool, auth)
```

当前 Hermes 的工具执行路径相对单一。引入策略模式后，不同类型的工具（REST API、本地脚本、gRPC 服务等）可以有各自优化过的执行路径。

### 4.4 优先级二：自然语言权限边界

ACI 的 `custom_instructions` + LLM 违规检测是低成本高收益的安全机制。Hermes 可以这样实现：

```python
# 在工具执行前
violation = await check_violation(
    tool_name="send_email",
    tool_input={"to": "external@gmail.com", "body": "..."},
    nl_policy="只允许向 @nousresearch.com 域名的邮箱发送邮件"
)
if violation:
    raise ToolExecutionDenied(reason=violation.justification)
```

**价值**：这比静态的 RBAC 规则灵活得多，可以处理"只允许在工作时间执行危险操作""不允许发送超过 500 字的输出"等语义级约束。而且 ACI 的实践经验表明，用 `gpt-4o-mini` 做违规检测的成本极低（每次约 $0.00015）。

### 4.5 优先级三：意图驱动的工具发现

当 Hermes 的工具列表增长到 50+ 时，将所有 tool definition 塞进 system prompt 将变得不现实。ACI 的向量搜索方案值得参考：

1. **离线**：为每个工具生成 embedding（name + description + parameters 的向量）
2. **在线**：用户请求到来时，先提取意图 embedding，用余弦相似度返回 top-K 工具
3. **优雅降级**：如果用户明确指定工具名，则跳过搜索直接使用

对于 Hermes 当前的工具规模（~20 个），这可能还不是刚需。但考虑到工具生态的增长趋势，提前架设这套基础设施是明智的。

### 4.6 优先级三：统一 MCP Server 适配

ACI 通过 `aci-mcp` 包实现了与 MCP 生态的互操作。Hermes 也可以考虑：

- **Hermes-as-MCP-Client**：让 Hermes 能够连接到其他 MCP Server，扩展工具能力
- **Hermes-as-MCP-Server**：将 Hermes 的工具能力暴露为 MCP Server，让 Claude Desktop / Cursor 等 IDE 能直接使用 Hermes 的工具链

后者尤其有价值——Hermes 已经集成了大量的能力（文件操作、代码执行、搜索等），将这些能力封装为 MCP Server，可以让 Hermes 的工具生态辐射到整个 MCP 生态。

### 4.7 借鉴优先级总结

| 特性 | 实现难度 | 收益 | 建议优先级 |
|------|---------|------|-----------|
| 声明式工具注册（YAML/JSON） | 低 | 高 | **P0 立即采纳** |
| visible/invisible 参数分离 | 低 | 高 | **P0 立即采纳** |
| 多执行器策略模式 | 中 | 中 | **P1 短期规划** |
| 自然语言权限边界 | 中 | 高 | **P1 短期规划** |
| 意图驱动工具发现 | 高 | 中（当前规模下） | **P2 中期规划** |
| MCP Server 适配 | 中 | 高 | **P2 中期规划** |

---

## 附录：ACI 核心数据模型

```
Organization (多租户顶层)
  └── Project (逻辑容器，包含配额管理)
        ├── Agent (API 调用者，有 allowed_apps + custom_instructions)
        │     └── APIKey (加密存储，唯一关联一个 Agent)
        ├── AppConfiguration (App 的租户级配置，可覆盖 security scheme)
        │     └── App (元数据 + security_schemes + categories)
        │           └── Function (参数定义 + embedding + protocol_data)
        └── LinkedAccount (租户在某 App 上的认证凭据，per linked_account_owner_id)
```

---

*拆解日期：2026-05-31 · 仓库版本：main 分支最新*
