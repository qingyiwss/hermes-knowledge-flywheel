# Wiki Log

> 所有 wiki 操作按时间记录。仅追加。
> 格式：`## [YYYY-MM-DD] 操作 | 主题`

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

## [2026-05-29] ingest | CodeGraphContext MCP 代码图谱
- 飞轮第三轮：扫描 MCP 工具/代码质量/工作流/浏览器自动化 4 方向
- 拆解 CodeGraphContext（⭐3.5K）→ [[codegraphcontext-mcp-tools]]
- 8 个 MCP 工具 + AST→图→死代码检测 → pre-commit verifier 架构蓝图

## [2026-05-29] ingest | TradingAgents + claude-obsidian + github 推送优化
- 飞轮第一轮正式运行：拆解 TradingAgents（⭐80K）→ [[tradingagents-multi-agent-architecture]]
- 能力审计扫描：claude-obsidian（⭐5.7K）→ [[claude-obsidian-architecture]]
- 知识飞轮升级到 v2.0：新增 Hot Cache、Wiki Lint、Delta 追踪、方法论路由
- 修复 GitHub 推送流程：诊断 Clash 代理阻断 api.github.com，创建 github-push-china skill
