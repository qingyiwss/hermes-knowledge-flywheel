# 最近会话

> 自动归档。每次会话结束追加。新会话开始必读。

## [2026-05-29] 知识飞轮 6 轮全速运转
**做了什么**
- 飞轮第1轮：TradingAgents（⭐80K）→ Reasonix 辩论机制
- 飞轮第2轮：claude-obsidian（⭐5.7K）→ 飞轮升级 v2.0 + 创建 github-push-china skill
- 飞轮第3轮：CodeGraphContext（⭐3.5K）→ pre-commit verifier 蓝图
- 飞轮第4-6轮：Token 优化三连（LLMLingua 压缩 / GPTCache 缓存 / LiteLLM 路由）
- 建立元规则：同一问题两次 → 立刻沉淀 skill；用户审批全免
- 飞轮触发词："启动飞轮" / "飞轮扫描" / "能力审计"

**学到了什么**
- GitHub 推送：github.com 直连不稳，api.github.com 稳定 → API 推送作为容灾；token 用 write_file 存文件最可靠
- 飞轮笔记格式：6 个 frontmatter 字段，tags 首项 skill-learning，集成章节标题固定
- 能力演进：从单项目拆解 → 专题多轮扫描 → 全网对比审计，三级精度
- Token 优化三层：压缩（LLMLingua-2）→ 缓存（GPTCache）→ 路由（LiteLLM）

**待完成**
- P1: 混合检索脚本 + wiki-lint + hot cache 自动更新
- P1: pre-commit verifier agent
- P2: QuantDinger Agent Gateway
- 公司名字未确定

## [2026-05-29] 搭建AI指挥官系统 + 公司注册
**做了什么**
- 创建 project-commander 技能、配置 cc+reasonix、初始化 Obsidian Wiki
- 主模型切 deepseek-v4-pro，生成公司注册法律模板

**学到了什么**
- hermes fallback add 交互式不可自动化，config.yaml 系统保护区

## [2026-05-31] 微信会话 — 双引擎重构 + 系统清理 + 微信接入

**主题**：多任务并行
1. QQ Bot 对接失败（沙箱环境无法调用正式 API）→ 换微信对接 ✅
2. 翻墙修复（CordCloud 订阅更新，ClashX 清理远程托管） ✅
3. Mac 系统深度清理（清理孤儿残留 ~5GB，修复启动项，整理环境） ✅
4. 双引擎职责重构（Hermes=理解+调度+验收，CC=执行） ✅
5. 知识库飞轮 3 轮（补全 34 页 frontmatter，收录 2 个孤立页面） ✅
6. 监控体系搭建（wxwatch / ccwatch / proxy 工具链） ✅

**决策**：
- QQ 被弃用，微信正式成为通信主通道
- Claude Code 无法在当前 macOS 10.15 运行，需升级系统
- Hermes 确认了"完全理解需求后再分发"的硬约束
