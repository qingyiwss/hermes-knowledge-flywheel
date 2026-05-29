# 进化日志

> 知识飞轮的成长轨迹。每次拆解一个项目后追加。

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
