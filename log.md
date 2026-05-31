# Wiki Log

> 所有 wiki 操作按时间记录。仅追加。
> 格式：`## [YYYY-MM-DD] 操作 | 主题`

## [2026-05-31] create | code-review-graph 拆解

- 拆解 tirth8205/code-review-graph（⭐17,731）
- 写入 concepts/code-review-graph.md
- 更新 index.md（总页数 22→23）
- 深度分析四大核心能力：Tree-sitter AST 解析、GraphRAG 知识图谱、MCP 30 工具、秒级增量更新
- 爆炸半径 100% 召回 + 38x–528x token 压缩 + 12+ 平台自动安装
- 输出 Hermes pre-commit verifier 三阶段落地路线
- 数据来源：GitHub API（仓库元数据 + README + graph.py）+ PyPI 页面

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
