# 进化日志

> 知识飞轮的成长轨迹。每次拆解一个项目后追加。

## [2026-05-31] 双引擎职责分工 — NΞXUS Hermes + Claude Code 硬分工

- **来源：** 内部沉淀（用户需求驱动）
- **学到了什么：** 双 Agent 协作的最大风险不是能力不足，而是责任模糊。用"产出类型"一刀切（产出=代码变更→CC，产出≠代码变更→Hermes）消除所有灰色地带。4阶段防作弊工作流（需求理解→拆解分发→三重验证→终验报告）确保不听见就信。每条声明必须有物证，每项验证必须实际执行。
- **能力提升：** Hermes 从"代码执行者"升级为"全链路 PM"——需求理解、任务拆解、验收把关、终验汇报；CC 降为纯粹的代码工人。防作弊规则覆盖虚构内容、虚假测试、跳过验收等常见 AI Agent 偷懒路径。
- **下一步：** 在实际项目中验证双引擎协作流程，收集 CC 违规案例优化防作弊规则。

## [2026-05-29] cc+re 共同成长计划 — Aider/QUANTAXIS/A2A

- **来源：** GitHub 扫描（Aider 26K / QUANTAXIS 8.4K / Google A2A 15K）
- **学到了什么：** Aider 的 SEARCH/REPLACE 编辑格式 + Repo Map 可大幅提升 cc 的代码修改精度；QUANTAXIS 的事件驱动回测 + 夏普/Calmar 归因可直接移植到 re 的估值定投；A2A 的 Agent Card + Task 协议是三人团队统一通信接口的蓝图。
- **能力提升：** 飞轮从"我一个人的知识库"升级为"三人共享知识库"——cc 有了 CLAUDE.md 自动加载 Wiki，re skill 增加了飞轮知识链接。
- **下一步：** 将 A2A 协议落地为 Hermes↔cc↔re 的统一接口；让 cc 用 Aider 的编辑策略改写 Reasonix 代码。

## [2026-05-29] Token Smart Pipeline + 团队协作五连拆

- **来源：** 自研 + GitHub 扫描（MetaGPT/PR-Agent/AFFiNE/GitButler/Plane）
- **学到了什么：** 将 LLMLingua+GPTCache+LiteLLM 三层落地为 pipeline（`pipe.ask()` 一行调用）；MetaGPT 的 SOP+Environment 消息总线是 Agent 协作的黄金范式；PR-Agent 的 8 Agent Pipeline 可复用到 Hermes 审查流程；AFFiNE 的 CRDT 同步机制解决了离线协作的数据一致性问题；GitButler 的虚拟分支可让 Hermes 多任务并行隔离；Plane 的三层任务模型适合 Agent 任务分解。
- **能力提升：** Token 优化三层落地为可运行代码；指挥官模式 v1.0→v2.0（强制派发+能力矩阵+违规自检）；团队协作方向积累 5 篇 Wiki。
- **下一步：** 将 MetaGPT 的 Environment 消息总线引入 Hermes subagent 通信；实现 pre-commit verifier（借鉴 PR-Agent 的 Pipeline 模式）。

## [2026-05-29] LiteLLM AI 网关

- **来源：** https://github.com/BerriAI/litellm
- **学到了什么：** 100+ LLM 统一 OpenAI 格式调用；Router 自动按成本/延迟选择模型并自动 fallback；每次调用带 response_cost 追踪实际花费；预算硬限制超限自动 429；P95 延迟仅 8ms @ 1K RPS；虚拟密钥 + guardrails 生产就绪。Stripe/Netflix 生产使用。
- **能力提升：** Hermes 可实现按任务复杂度自动路由（flash 简单任务 / pro 复杂决策），每次对话末尾显示 token 消耗和费用，月预算告警 + 自动降级。
- **下一步：** 评估 litellm Router 替代 Hermes 当前的模型选择逻辑；实现成本追踪回调。

## [2026-05-29] GPTCache 语义缓存

- **来源：** https://github.com/zilliztech/GPTCache
- **学到了什么：** 请求→嵌入→相似度搜索→命中则返回缓存→未命中调 LLM→存入缓存；支持多种嵌入后端（OpenAI/HuggingFace/本地）和存储后端（Redis/SQLite/Milvus）；相似度阈值 + LRU 淘汰；与 LangChain/LlamaIndex 深度集成。
- **能力提升：** 飞轮 GitHub API 搜索可缓存 ~80%；相似错误诊断直接复用之前方案；skill 文档查询缓存 ~40% 冷启动开销。
- **下一步：** 评估在 Hermes tool 调用层加缓存层；优先对 web_search 和 search_files 做语义缓存。

## [2026-05-29] LLMLingua Prompt 压缩

- **来源：** https://github.com/microsoft/LLMLingua
- **学到了什么：** 小 LM 计算每个 token 困惑度→移除低信息量 token→最高 20x 压缩；LLMLingua-2 用 BERT 做 token 分类，3-6x 更快且任务无关；LongLLMLingua 解决长文本"迷失中间"问题；三个 ACL/EMNLP 论文背书。
- **能力提升：** 系统 prompt（AGENTS.md + memory）可压缩 ~70%；飞轮扫描的长 README 先压缩再分析节省 ~80% 上下文；历史对话压缩替代粗暴截断保持 ~50% 更多上下文。
- **下一步：** 评估 LLMLingua-2 在 Hermes 的 skill/memory 注入前做轻量压缩；测试压缩后对指令遵循的影响。

## [2026-05-29] CodeGraphContext 代码图谱 MCP 工具

- **来源：** https://github.com/CodeGraphContext/CodeGraphContext
- **学到了什么：** AST 解析代码生成图节点（Repository/File/Module/Class/Function）+ 关系边（CONTAINS/CALLS/IMPORTS/INHERITS），通过 MCP 暴露 8 个工具（find_code、analyze_relationships 含 15 种查询类型、find_dead_code、cyclomatic_complexity、watch_directory）；异步 job_id 模式处理长索引不阻塞；多数据库后端（Neo4j/FalkorDB/Kuzu）统一接口切换；配套 AI 系统 Prompt 定义了"优先查图、不要猜"的核心原则。
- **能力提升：** pre-commit verifier 有了清晰的架构蓝图——用 Python `ast` 模块 + dict 替代 Neo4j，轻量实现死代码检测、调用链分析、复杂度告警；"先查后答"原则可直接融入 Hermes 的代码审查流程。
- **下一步：** 用 stdlib ast 实现简化版 pre-commit verifier agent；集成到 git hook 中自动触发。

## [2026-05-29] claude-obsidian 知识管理架构

- **来源：** https://github.com/AgriciDaniel/claude-obsidian
- **学到了什么：** 15 个专门技能覆盖知识管理全流程（摄入→检索→查询→保存→自查→自主研究）；Hot Cache 用 ~500 词摘要桥接跨会话上下文，解决"每次重头开始"的问题；混合检索（BM25 + 余弦重排）比纯 grep 精准一个量级；10 项 Lint 检查让 Wiki 自动保持健康；Delta 追踪按文件 hash 跳过已处理源，避免重复工作；方法论路由支持 4 种组织模式（Generic/LYT/PARA/Zettelkasten）可插拔切换；10 原则 Think 框架为复杂决策提供结构化思维流程。
- **能力提升：** 知识飞轮从 v1.0 升级到 v2.0，新增 Hot Cache、Wiki Lint、Delta 追踪、3 级查询深度、方法论路由；Hermes skill 体系从"功能堆叠"转向"流程闭环"；搜索能力从纯关键词匹配升级为语义+关键词混合检索。
- **下一步：** 实现 `retrieve.py` 混合检索脚本；将 10 项 Lint 检查落地为可执行脚本；创建 Hot Cache 自动更新流程；研究 claude-obsidian 的 autoresearch 模式为飞轮增加自主扫描能力。

## [2026-05-29] TradingAgents 多智能体交易架构

- **来源：** https://github.com/TauricResearch/TradingAgents
- **学到了什么：** 多智能体辩论机制（Bull/Bear 对立研究员 + 三方风控辩论）可有效降低单模型确认偏误；双 LLM 策略（廉价模型扫描 + 昂贵模型决策）是 token 经济学的最佳实践；交易记忆闭环（pending → 反射 → resolved）让系统从历史错误中自我修正；结构化输出 + 五档评级让决策粒度从二值升级到五档，解析用确定性正则而非额外 LLM 调用。
- **能力提升：** Reasonix 可从单路径分析升级为辩论式多视角决策；新建交易记忆模块让回测结果反哺策略优化；双模型策略直接落地（flash 扫描 + pro 决策）；配置系统可引入 `_ENV_OVERRIDES` 映射表模式。
- **下一步：** 在 Reasonix 回测引擎中实现 bull/bear 双参数并行辩论；探索 LangGraph 替代当前线性脚本的可行性。

## [2026-05-29] 需求分析专题 — 3篇
- **来源：** doorstop (629⭐) + MetaGPT (68K⭐) + Robot Framework (11.7K⭐)
- **学到了什么：** 需求管理三环节——管理(doorstop Git原生)、分析(MetaGPT SOP驱动)、验证(Robot Framework 关键字驱动)。三者可组合：doorstop存需求→MetaGPT生成实现→Robot验证回归。
- **能力提升：** Nexus监控系统可借鉴doorstop的文件式任务存储+SOP模板化输出+Robot自动化验收。
- **下一步：** 将需求分析三件套融入Nexus独立项目设计。

## [2026-05-31] 双引擎重构 + 知识库清理（飞轮 3 轮）

**发现的问题**：
1. 34 个页面中 28 个缺少 `updated` 字段
2. 2 个孤立页面未收录到 index
3. 双引擎分工文档存在模糊地带（按产出分→按角色分才更精确）

**执行的改进**：
- 重写 nexus-dual-engine：Hermes=理解者+调度者+验收者，CC=执行者
- 加入防作弊规则表和"一票否决模糊地带"
- 补全 34 个页面的 frontmatter
- 收录 crochet-toy-market-research、toy-certification-guide 到 index

**学到的东西**：
- 代理协作的关键不是分工，是"禁止猜测"。当 Hermes 不完全理解需求时，分发给 CC 的任务必然跑偏
- 知识库需要定期巡检，指标：①frontmatter 完整度 ②死链 ③孤立页面
- 用户说的"飞轮"本质是：扫描→修复→反思→再扫描的闭环

## [2026-06-12] Token 优化恢复 + SOUL.md 激活 — 云端迁移后优化参数丢失的教训

- **来源：** 用户需求驱动（优化 token 消耗和执行效率）
- **学到了什么：** 网关重启后，config.yaml 中的某些优化参数会回退到默认值（threshold_pct: 10, child_timeout: 600），必须手动重新设置。三个参数修复即可恢复 ~4,100 tokens/轮的节省。SOUL.md 需要 `hermes config set personality SOUL.md` 才能生效，仅放在 ~/.hermes/ 并不会自动加载。
- **能力提升：** 3 个配置修复（threshold_pct 3%, child_timeout 300, max_iterations 15）+ personality 激活，恢复约 48% 的提示词压缩效果。lessons-learned.md 新增"重启后检查配置"记录。
- **下一步：** 考虑用 cron 定期巡检优化参数是否偏离预期值，作为自动退化防御。

## [2026-06-12] CC (Claude Code) 安装 + DeepSeek API 配置 — NΞXUS 双引擎正式合体

- **来源：** 用户需求（恢复知识库后要求安装CC并配上DeepSeek API）
- **学到了什么：** DeepSeek 提供 Anthropic 兼容 API（`https://api.deepseek.com/anthropic`），Claude Code 可以原生接入，无需代理。关键环境变量 6 个：`ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`, `ANTHROPIC_DEFAULT_OPUS/SONNET/HAIKU_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL`, `CLAUDE_CODE_EFFORT_LEVEL`。包装脚本 `hermes-cc.sh` 封装了所有配置，Hermes 直接用 bash hermes-cc.sh -d <dir> "任务" 派发。
- **能力提升：** NΞXUS 双引擎正式上线——Hermes（指挥官）+ CC（代码工人），职责清晰分工。CC 有专属 CLAUDE.md 明确权限边界。
- **下一步：** 第一个实际代码任务派发给 CC，验证双引擎协作流程。

## [2026-06-12] 搜索优化 — DDGS 后端配置 + Hermes v0.16 文档学习

- **来源：** 用户需求（优化网络环境和搜索能力）+ Hermes v0.16 升级后学习官方文档
- **学到了什么：**
  - Hermes web 搜索支持 7 个后端，可通过 `web.search_backend` 配置，**DDGS (DuckDuckGo)** 是唯一无需任何 API Key 的免费后端，`pip install ddgs` 即可用
  - Hermes 支持 **per-capability 配置**：`web.search_backend` 和 `web.extract_backend` 可独立设置，搜索用免费的 DDGS、提取用 Firecrawl 等
  - 这台 LAX 服务器 **Google 直连 245ms**，没有网络限制，之前的 Tor/Clash 代理完全不需要
  - Hermes v0.16 的新功能：Tool Gateway、firecrawl 集成、ddgs 支持、per-capability 搜索配置
  - 更新了 skills 数据：hermes-agent 技能记录的最新 CLI 命令（cron 子命令更新、sessions 命令更新等）
- **能力提升：** 搜索从"默认后端 + Bing curl 补丁"升级为"DDGS 免费高质量搜索"，中英文搜索结果质量显著提升。Hermes 知识库技能内容保持与 v0.16 文档同步。
- **下一步：** 评估是否需要配置 `web.extract_backend` 提升 URL 内容提取质量

## 紧急规则（2026-06-12）

**触发词「魏松山」= 上下文丢失信号**
- 当收到消息只包含"魏松山"时 → 立即从 all_concepts 中重建上下文，继续当前任务
- 每次飞轮完成后必须推送到 GitHub：`git add growth-log.md lessons-learned.md wiki/hot.md && git commit -m "docs: 飞轮#N 同步 — <摘要>" && git push`
