# Wiki Log

> 所有 wiki 操作按时间记录。仅追加。
> 格式：`## [YYYY-MM-DD] 操作 | 主题`

## [2026-06-02] create | Chrome 浏览器方案 — 三方案 + 踩坑记录
- 新增 [[chrome-solution]] — 真实 Chrome CDP 桥接（navigator.webdriver=false）+ headless + --disable-ipv6 + GitHub API
- 落地：chrome-bridge.py 脚本 + .env 配置更新 + wiki-index.json 注册
- 6 个踩坑：IPv6泄露、Tor出口IP、zombie agent-browser、CloakBrowser Catalina不兼容、undetected-chromedriver间歇性、headless锁真Chrome
- 测试 12 种免费方案，最终选定 github API + chrome-bridge 双轨

## [2026-06-02] 飞轮×3 | browser-use + activepieces + mcp-use 三连拆解
- 扫描 GitHub Trending（AI Agent / 浏览器自动化 / MCP 方向）
- [[browser-use-agent]] — 96K⭐ AI Agent 浏览器自动化，Playwright 封装 + Cloud Stealth
- [[activepieces-mcp-workflow]] — 22.5K⭐ 开源 Zapier，280+ Pieces 自动转 MCP Server
- [[mcp-use-framework]] — 10K⭐ 全栈 MCP，核心创新 MCP Apps（带 UI Widget 的工具）
- 审计修复：22 个反斜杠路径 + 新增 3 个孤儿文件到索引
- 索引：33 → 38 条目，概念文件：50 → 50（净增 0，新增 3 篇抵消了索引补录的 2 篇 + 1 篇新概念）

## [2026-05-31] 飞轮1/5 | Context注入审计 + P0优化落地
- 新增 [[token-injection-audit]] — 量化每轮 10,245 tokens 固定注入，Tool Schemas 占 85%
- 落地：禁用 5 个闲置 toolset (spotify/homeassistant/video/image_gen/video_gen)
- 落地：tool_search.threshold_pct 10→5，show_cost=true，token_analytics=true

## [2026-05-31] 飞轮2/5 | CC上下文瘦身
- 新增 [[cc-context-slim]] — CLAUDE.md 97行→26行，gstack技能表压缩+懒加载
- 落地：CLAUDE.md v2.5 精简到 26 行 1,381 chars，CC 验证 38 个 gstack 技能全识别

## [2026-05-31] 飞轮3/5 | 系统提示词+工具描述优化
- 新增 [[system-prompt-slim]] — SOUL.md 效率 persona + threshold 5→3% + child_timeout 600→300
- 落地：SOUL.md 写入中文效率导向 persona，工具搜索阈值降至 3%

## [2026-05-31] 飞轮4/5 | Memory 压缩
- 新增 [[memory-compression]] — 代理条目 3→1，删除过期订阅链接，节省 84%

## [2026-05-31] 飞轮5/5 | Token 实时监控+自适应降级
- 新增 [[token-monitoring-system]] — token-monitor.py + 每日 22:00 cron 报告 + fallback_providers 配置
- 落地：监控脚本从 state.db 读数据，cron job 自动推送日报

## [2026-05-31] create | LangGraph 有状态Agent编排框架拆解

- 拆解 langchain-ai/langgraph（⭐33,415）
- 写入 concepts/langgraph-stateful-agents.md
- 更新 index.md（总页数 27→28）
- 深度分析五大核心能力：StateGraph Reducer 状态管理（Annotated 标注合并策略）、条件分支（Literal 类型安全路由）、循环（环形边+Send Map-Reduce 并行）、Human-in-the-loop（interrupt+Command/resume）、Checkpointer 持久化（每步自动快照+时间旅行）
- 重点输出：langgraph 有状态编排 vs crewAI 角色化编排 vs autogen 消息编排三角对比
- NΞXUS 防作弊流水线对接：每条验证步骤 = 一个 Graph 节点 + 每步 Checkpoint 快照 + 失败回滚到上一个 Checkpoint
- 关键发现：LangGraph 的 Reducer 设计区别于所有 Agent 框架——不是管 Agent 怎么写，而是管写入同一状态时怎么合并；Checkpoint 是 Human-in-the-loop 的绝对前提
- 数据来源：GitHub raw（README + state.py 1964行 + types.py + checkpoint/base/__init__.py）

## [2026-05-31] create | Microsoft AutoGen 多Agent框架拆解

- 拆解 shuvonsec/claude-bug-bounty（⭐2,340）
- 写入 concepts/claude-bug-bounty-security.md
- 更新 index.md（总页数 27→28）
- 深度分析六大核心能力：20种Web2漏洞检测类型、10种Web3合约漏洞、8个AI Agent、23个Slash命令、8阶段侦察引擎、5阶段非线性渗透工作流
- 提取核心流程：侦察信息收集（50+工具编排）→ 自主渗透测试（5阶段+autopilot三种模式）→ 漏洞验证（7问门控+4道提交关）→ 报告生成（报告模板+CVSS 3.1）
- 重点输出 NΞXUS CC 代码安全审查集成方案：CC 写完代码 → Hermes 自动触发安全扫描 → 门控决策（PASS/WARN/FAIL）→ 结合 qodo-cover + code-review-graph 形成完整验收流水线
- Hermes Skill 封装：cc-security-gate（静态分析+密钥检测+依赖漏洞+代码模式）
- 借用机制：7问门控、密钥检测管道、CVE情报、semgrep多语言规则、永不提交清单、条件有效链、认证感知扫描
- 数据来源：GitHub raw（README + SKILL.md ×3 + hunt.py + recon_engine.sh + vuln_scanner.sh + triage-validation SKILL.md）

## [2026-05-31] create | Microsoft AutoGen 多Agent框架拆解

- 拆解 microsoft/autogen（⭐58,553）
- 写入 concepts/autogen-multi-agent-framework.md
- 更新 index.md（总页数 25→26）
- 深度分析五大核心能力：Agent对话模式（增量状态+发布订阅）、工具调用（Tool协议+Workbench抽象）、代码执行沙箱（Docker隔离+审批函数）、多Agent编排（Selector/RoundRobin/AgentTool/Handoff）、终止条件（可组合状态机）
- 重点输出：与 A2A 三角对比 + NΞXUS Hermes↔CC 通信升级方案（4个阶段：Pydantic消息类型 → asyncio Queue Topic总线 → Selector编排+Handoff → 代码沙箱）
- 关键发现：SelectorGroupChat的LLM选发言人比A2A被动等待更适合NΞXUS主动式多Agent编排；AgentTool模式让Agent可被其他Agent当工具调用
- 风险提示：AutoGen已进入maintenance mode，核心逻辑可借鉴但新功能应参考MAF
- 数据来源：GitHub raw（README + 9个核心源文件：AssistantAgent / BaseGroupChat / SelectorGroupChat / RoundRobinGroupChat / CodeExecutorAgent / messages / CoreAgent / Handoff / BaseTool）

## [2026-05-31] create | qodo-cover AI测试生成拆解

- 拆解 qodo-ai/qodo-cover（⭐5,408）
- 写入 concepts/qodo-cover-ai-testing.md
- 更新 index.md（总页数 25→26）
- 深度分析四大核心能力：CoverAgent 编排器、迭代式测试生成、覆盖率解析闭环、全仓模式
- 重点输出 NΞXUS CC 产出验证流程：CC 写完代码 → Hermes 编排 qodo-cover → 自动生成测试 → 验证覆盖率 ≥ 80%
- 成本：约 $0.001/次（gpt-4o-mini），Record/Replay 后零成本
- 数据来源：GitHub raw（README + pyproject.toml + cover_agent/*.py + prompt TOML + docs）

## [2026-05-31] create | code-review-graph 拆解

- 拆解 tirth8205/code-review-graph（⭐17,731）
- 写入 concepts/code-review-graph.md
- 更新 index.md（总页数 22→23）
- 深度分析四大核心能力：Tree-sitter AST 解析、GraphRAG 知识图谱、MCP 30 工具、秒级增量更新
- 爆炸半径 100% 召回 + 38x–528x token 压缩 + 12+ 平台自动安装
- 输出 Hermes pre-commit verifier 三阶段落地路线
- 数据来源：GitHub API（仓库元数据 + README + graph.py）+ PyPI 页面

## [2026-05-31] create | 飞轮第3轮：langgraph + claude-bug-bounty + harbor 三连拆

- langgraph（⭐33,415）→ concepts/langgraph-stateful-agents.md（子Agent拆解）
- claude-bug-bounty（⭐2,340）→ concepts/claude-bug-bounty-security.md（子Agent拆解）
- harbor（⭐3,017）→ concepts/harbor-llm-stack.md（手动拆解，raw超时）
- 更新 index.md（总页数 27→29）、hot.md、log.md、wiki-index.json
- NΞXUS 对接：StateGraph 防作弊流水线 + CC安全审查门控 + 模型统一配置层

## [2026-05-31] create | 飞轮第2轮：autogen + qodo-cover + crewAI 三连拆

- autogen（⭐58,553）→ concepts/autogen-multi-agent-framework.md
- qodo-cover（⭐5,408）→ concepts/qodo-cover-ai-testing.md
- crewAI（⭐52,494）→ concepts/crewai-role-based-agents.md（手动拆解，子Agent超时）
- 更新 index.md（总页数 24→27）、hot.md、log.md
- 深度分析：SelectorGroupChat 编排、覆盖率闭环、Role/Goal/Backstory 角色模式
- NΞXUS 对接：Selector编排+Backstory模板+Flow防作弊流水线+测试自动验证

## [2026-05-31] create | ACI 工具调用平台拆解

- 拆解 aipotheosis-labs/aci（⭐4,793）
- 写入 concepts/aci-tool-calling-platform.md
- 更新 index.md（总页数 23→24）、hot.md
- 600+工具声明式注册（app.json + functions.json）、7层安全检查链、向量语义工具发现
- 与 MCP 8 维对比，结论：互补而非竞争
- Hermes 借鉴方案：声明式注册 + visible/invisible 分离 + NL 权限边界
- 数据来源：GitHub API（20+ 文件：README + main.py + acl.py + processor.py 等）

## [2026-05-31] create | Agent Governance Toolkit 拆解

- 拆解 microsoft/agent-governance-toolkit（⭐3,481）
- 写入 concepts/agent-governance-toolkit.md
- 更新 index.md（总页数 21→22）
- 深度分析三大核心能力：策略执行、零信任身份、沙箱隔离
- 输出 NΞXUS 双引擎防作弊对接方案（4 Phase）
- 数据来源：README + 3 份 RFC 2119 规范（Policy Engine / Identity & Trust / Hypervisor） + OWASP 架构文档

## [2026-05-31] create | 双引擎职责分工

- 内部沉淀：NΞXUS Hermes + Claude Code 硬分工与防作弊机制
- 写入 concepts/nexus-dual-engine.md
- 更新 index.md（总页数 20→21）、hot.md、growth-log.md、wiki-index.json
- 4 阶段工作流 + 三重验证 + 防作弊规则表

## [2026-05-29] create | Wiki 初始化
- 在 Obsidian Vault 中创建 wiki 结构
- SCHEMA.md：定义三大领域（投资/AI自媒体/公司运营）
- index.md：初始 8 个页面索引
- 目录结构：raw/ entities/ concepts/ comparisons/ queries/

## [2026-05-29] ingest | 飞轮第一轮扫描
- 扫描三个方向（AI Agent / CLI / Prompt），精选 2 个项目
- 拆解 shareAI-lab/learn-claude-code（63k⭐）→ [[harness-engineering]]
- 拆解 Panniantong/Agent-Reach（20k⭐）→ [[agent-reach-internet]]
- 更新 index.md（+2 页面），更新 growth-log（轮次1）

## [2026-05-29] ingest | Token 优化三连
- 飞轮第 4-6 轮：LLMLingua（⭐6.2K，Prompt 压缩 20x）+ GPTCache（⭐8K，语义缓存）+ LiteLLM（⭐49K，AI 网关）
- 三层 token 优化架构：压缩层（LLMLingua-2）→ 缓存层（GPTCache）→ 路由层（LiteLLM Router）
- 新增 3 篇 Wiki 笔记，index 总页数 5→8
- GitHub 直连不稳定时切换 API 推送方案（write_file 存 token + Python 读文件）
- 发现 github.com 不定时不可达但 api.github.com 稳定 → API 推送作为容灾方案

## [2026-05-29] ingest | CodeGraphContext MCP 代码图谱
- 飞轮第三轮：扫描 MCP 工具/代码质量/工作流/浏览器自动化 4 方向
- 拆解 CodeGraphContext（⭐3.5K）→ [[codegraphcontext-mcp-tools]]
- 8 个 MCP 工具 + AST→图→死代码检测 → pre-commit verifier 架构蓝图

## [2026-05-29] ingest | TradingAgents + claude-obsidian + github 推送优化
- 飞轮第一轮正式运行：拆解 TradingAgents（⭐80K）→ [[tradingagents-multi-agent-architecture]]
- 能力审计扫描：claude-obsidian（⭐5.7K）→ [[claude-obsidian-architecture]]
- 知识飞轮升级到 v2.0：新增 Hot Cache、Wiki Lint、Delta 追踪、方法论路由
- 修复 GitHub 推送流程：诊断 Clash 代理阻断 api.github.com，创建 github-push-china skill

## [2026-05-31] 重构双引擎 | NΞXUS

**操作**：重写 nexus-dual-engine.md，把 Hermes 和 Claude Code 的职责从之前的"按产出类型分"改为"按角色分"：
- Hermes = 理解者 + 调度者 + 验收者（8项硬职责）
- Claude Code = 执行者（6项硬职责）
- 加入"一票否决模糊地带"：看到"优化一下/搞定/类似xxx/你看着办" → 追问不猜测
- 加入防作弊规则表：违规→惩罚

**原因**：之前的硬分工只看"产出是代码还是非代码"，但关键问题是 Hermes 没理解清楚需求就分发任务，导致 CC 乱做。

**效果**：现在有明确的 4 阶段流程，阶段 0 强制 Hermes 确认 5 问后才能进入下一阶段。
---
## [2026-06-04] 飞轮 4 轮 — 内容去AI味

**扫描**：GitHub trending → lynote-ai/humanize-text (⭐1069)
**拆解**：四种方法论（翻译链/LLM改写/检测闭环/混合引擎）
**沉淀**：
- 新增 [[ai-text-humanization]] — AI文本人味化知识
- 更新 zhihu-content 技能：去推广声明、去AI味写作原则、模板句替换表
- 保存淘宝联盟凭证到 .taobao-credentials
**学到**：去AI味不是让模型更聪明，是打破统计指纹——句长参差、temperature 1.2、AI高频词替换

