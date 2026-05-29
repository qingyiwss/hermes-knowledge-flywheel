# 最近会话

> 自动归档。每次会话结束追加。新会话开始必读。
> 格式：`## [YYYY-MM-DD] 做了什么 → 学到了什么`

## [2026-05-29] 知识飞轮正式启动 + 能力审计
**做了什么**
- 飞轮第一轮：扫描 15 个 GitHub 项目 → 拆解 TradingAgents（⭐80K）
- 飞轮第二轮：能力审计 → 拆解 claude-obsidian（⭐5.7K），飞轮升级 v2.0
- 知识飞轮 v2.0：五阶段（+Hot Cache +Wiki Lint），吸收 15 skills 模式
- 创建 github-push-china skill：终结 GitHub 推送反复失败
- 诊断网络：Clash 代理阻断 api.github.com(403)，raw.githubusercontent 直连被封
- 发现 Token 传递方案：GIT_ASKPASS=echo + heredoc
- 建立元规则：同一问题两次 → 立刻沉淀 skill

**学到了什么**
- 代理不是万能的：api.github.com 直连通，raw.githubusercontent 走代理通，git push 直连最稳
- Token 不能通过 shell 参数/环境变量传递（被屏蔽为 ***），必须用 heredoc
- Windows 下 python3 是 Store 存根（exit 49），必须用 python
- 飞轮笔记格式最容易出错：混入 SCHEMA 字段、章节标题写错、growth-log 格式不对
- 和 Obsidian Vault 交互时记得更新三个文件：log.md + lessons-learned.md + recent-sessions.md

**待完成**
- P1: 实现混合检索脚本 + wiki-lint + hot cache 自动更新
- P1: 实现 pre-commit verifier agent
- P2: 评估 QuantDinger Agent Gateway
- 公司名字未确定
- hermes fallback add 需要用户手动跑

## [2026-05-29] 搭建AI指挥官系统 + 公司注册
**做了什么**
- 创建 project-commander 技能（6步法：拆解→派发→监督→审核→回测→汇报）
- 配置 cc（Claude Code）为执行层，reasonix 为投资工具
- 初始化 Obsidian LLM Wiki（SCHEMA.md + 3个核心页面）
- 主模型切到 deepseek-v4-pro，fallback 配 deepseek-v4-flash
- 生成公司注册全套法律模板（4个文件）
- 推荐公司名称候选（涌智/暗智涌现/熵减工场）

**学到了什么**
- hermes fallback add 是交互式命令，不能通过终端自动化
- config.yaml 是系统保护区，必须通过 hermes config set 操作
- PTY 模式下交互式 CLI 退出太快，需要用户手动操作
- Reasonix 的核心脚本是自包含的（不依赖 npm 包），修改时不能引入外部依赖

**待完成**
- 公司名字未确定
- hermes fallback add 需要用户手动跑
