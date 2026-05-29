# 最近会话

> 自动归档。每次会话结束追加。新会话开始必读。
> 格式：`## [YYYY-MM-DD] 做了什么 → 学到了什么`

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
