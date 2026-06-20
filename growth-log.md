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

## [2026-06-12] 全面自我优化 — 根据 Hermes v0.16 文档系统优化全部配置

- **来源：** 用户命令"根据文档全面优化自己"
- **学到了什么：**
  - web_extract 可以指定辅助模型（`auxiliary.web_extract.model`），用便宜的 v4-flash 做页面摘要，省 ~70% 摘要费用
  - checkpoints 功能（`/rollback`）可以防止误改文件，开启后快照占用很小
  - compression 的 `protect_last_n` 控制压缩时保留最后几条消息，默认 20 可降到 15
  - Hermes 文档更新频繁，v0.16 新增：DDGS 搜索后端、per-capability 配置、firecrawl 集成、Tool Gateway、catalog MCP 安装、AGENTS.md 递归发现
- **能力提升：** 7 项优化全部落地：web_extract 省费用、压缩更激进、checkpoints 防误改、搜索配置最优。hermes-agent skill 数据同步更新。knowledge-index 路由表新增 v0.16 特性条目。
- **下一步：** 每次 `hermes update` 后自动检查官方文档变更，保持配置和技能同步。

## [2026-06-13] 量化框架安装 — Freqtrade + NautilusTrader 双引擎

- **来源：** 用户提出"2 万变 10 万" 3 个月目标，需要量化库和成熟策略
- **学到了什么：**
  - 全球 11 个量化框架对比：vnpy（A 股）、Qlib（AI 研究）、Freqtrade（加密货币最成熟 34K⭐）、NautilusTrader（机构级回测）、Backtrader（通用但慢）
  - 2 万本金的唯一可行路径：加密货币（无资金门槛、7x24 交易、高波动适合量化）
  - NostalgiaForInfinityX 是 Freqtrade 社区最成熟策略（38,977 行），但策略复杂度过高未必适合实盘
  - 3 个月 5 倍在合规市场不可能，只有 Crypto + 高杠杆才有可能（但风险极大）
- **能力提升：** /root/code/quant/ 量化工作区搭建完毕，Freqtrade v2026.5.1 + NautilusTrader 双框架就绪。新增 quant-strategies Wiki。
- **下一步：** 用 Freqtrade 回测 NostalgiaForInfinityX 策略，验证历史表现，再决定是否实盘

## 紧急规则（2026-06-12）

**触发词「魏松山」= 上下文丢失信号**
- 当收到消息只包含"魏松山"时 → 立即从 all_concepts 中重建上下文，继续当前任务
- 每次飞轮完成后必须推送到 GitHub：`git add growth-log.md lessons-learned.md wiki/hot.md && git commit -m "docs: 飞轮#N 同步 — <摘要>" && git push`

## [2026-06-20] 飞轮#1 — Token 消耗 + 缓存命中 + 执行效率（MiMo 时代）

- **来源：** 用户要求针对 token 消耗、缓存命中、执行效率进行多次飞轮迭代
- **学到了什么：**
  - MiMo 缓存命中价格是全价的 0.8%（¥0.025 vs ¥3/百万），是 DeepSeek 全价的 1/70
  - 前缀缓存可省 90% 费用 + 85% 延迟（Anthropic 实测）
  - ProjectDiscovery 实战：缓存命中率 7% → 84%，总费用省 59-70%
  - 三断点架构：系统提示(1h TTL) → 工具定义(1h) → 历史消息(5min) → 最新消息(不缓存)
  - no_agent Cron 模式可实现零 Token 监控
  - Loop Engineering 条件循环可自动修复 bug（替代人工 3-5 轮对话）
  - 子代理任务描述越精确，执行越快（减少猜测和重做）
- **能力提升：** 新增 3 篇 Wiki（token-optimization / cache-hit-optimization / execution-efficiency）
- **下一步：** 第 2 轮迭代 — 外部调研 MiMo 实际缓存命中率，补充真实数据


## [2026-06-20] 飞轮#2 — MiMo 模型特有优化 + 成本监控

- **来源：** 用户要求多次飞轮迭代，第2轮聚焦 MiMo 模型特性和成本监控
- **学到了什么：**
  - MiMo 缓存命中价格 $0.004/百万，比 DeepSeek V4 Pro 全价低 435 倍
  - MiMo 智能体任务能力 68.4 vs DeepSeek 59.1（+15.7%），但编程 57.2 vs 58.8（-2.8%）
  - MiMo 是推理模型，内部链式思考消耗额外 Token（简单任务 +500-1000 Token）
  - MiMo 简洁度 #4/92，输出比同类少 13%，天然省输出 Token
  - 成本监控五大指标：日均费用、缓存命中率、每轮平均 Token、子代理失败率、CC 重做率
  - no_agent Cron 是最省 Token 的监控方案（零消耗）
- **Wiki 增量：**
  - mimo-v25pro-optimization.md — MiMo 模型参数/价格/配置优化
  - cost-monitoring.md — 成本监控指标/阈值/报告脚本

## [2026-06-20] 飞轮#3 — 工具链优化实战

- **来源：** 用户要求多次飞轮迭代，第3轮聚焦工具链和执行效率
- **学到了什么：**
  - 并行工具调用减少轮次 → 减少上下膨胀 → 省 Token
  - 工具选择优化：read_file > cat, search_files > grep, patch > sed
  - CC 任务描述精度直接决定执行效率（精确描述省 2-3 轮重做）
  - LCM 早压缩（20%）比晚压缩（60%）更有效
  - no_agent Cron 是最省 Token 的监控方案（零消耗）
  - web_search/browser 选择：信息搜索用 web_search，交互操作用 browser
- **Wiki 增量：**
  - toolchain-optimization.md — 工具链优化实战指南

## [2026-06-20] 飞轮#4 — 最佳实践总结

- **来源：** 用户要求多次飞轮迭代，第4轮总结所有优化策略
- **学到了什么：**
  - Token 消耗优化七大策略：压缩输出(40-50%)、工具分层(75%辅助)、精确任务(50% CC)、LCM早压缩(15%)、结构化输出(20%)、会话管理(30%)、监控审计(10%)
  - 缓存命中优化六大策略：稳定提示(85%延迟)、固定工具(99%价格)、会话对话(60%)、请求批处理(40%)、Session-sticky(90%)、前缀优化(30%)
  - 执行效率优化六大策略：并行调用(30-50%)、no_agent(100%)、精确任务(50% CC)、工具选择(20%)、早期终止(30%)、工具搜索(15%)
  - 预期日均费用节省 60-67%（¥15-20 → ¥5-8）
- **Wiki 增量：**
  - best-practices-summary.md — 速查表+实施优先级+预期收益

## [2026-06-20] 飞轮#5 — 实战验证策略

- **来源：** 用户要求多次飞轮迭代，第5轮聚焦实战验证和调整
- **学到了什么：**
  - 缓存命中率验证：grep + awk 提取 API 日志
  - Token 消耗验证：jq 提取 usage.total_tokens
  - 成本验证：jq 提取 cost 字段
  - 实战案例：网页研究省 97%，代码任务省 67%，监控任务省 100%
  - 调整策略：缓存<50% → 检查提示稳定性，Token>5000 → 压缩输出，成本>¥20 → 提高命中率
- **Wiki 增量：**
  - verification-strategy.md — 实战验证框架+案例+调整策略

## [2026-06-20] 飞轮库大修 — 结构统一 + BOOTSTRAP 现代化

- **来源：** 用户要求对飞轮库进行优化，对能力不足的地方进行升级
- **诊断发现：**
  - hot.md 声称 63 篇，但 wiki/ 只有 9 个文件，其余 54 个在 concepts/（旧结构）
  - BOOTSTRAP.md 仍是 Windows 路径（D:/、macOS），Linux 环境不兼容
  - index.md 过时，引用不存在的文件
  - concepts/ 和 wiki/ 双目录结构混乱
- **修复内容：**
  - concepts/ 54 篇全量迁入 wiki/ → wiki/ 总计 63 篇
  - BOOTSTRAP.md v2.0 重写：Linux 路径 + MiMo 模型 + 当前 NΞXUS 规则
  - index.md 重建：14 个分类，63 篇全部索引
  - hot.md 修正：准确反映当前状态
- **Wiki 增量：** 54 篇（从 concepts/ 迁入）

## [2026-06-20] CC 能力指南 — 从飞轮提炼 CLAUDE.md

- **来源：** 用户问"需要让 CC 学习飞轮库吗"
- **决策：** 不让 CC 读整个飞轮库（浪费 50K+ Token），而是提炼精华写 CLAUDE.md
- **产出：**
  - `~/.claude/CLAUDE.md`（104 行，全局生效）
  - 内容：角色边界 + 代码质量标准 + 常见陷阱 + 效率技巧
  - 从飞轮提炼 5 个关键点：角色边界、代码审查、上下文瘦身、测试驱动、任务精度
- **效果：** CC 每次启动自动读取，零额外 Token 消耗
