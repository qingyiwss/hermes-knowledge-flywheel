# 经验教训

> 犯错即记，好做法即存。只追加不删除。
> 这是系统的"抗退化机制"。

## 工具和技巧

### ✅ 应该做的
- [2026-05-29] GitHub 推送用 `GIT_ASKPASS=echo` + heredoc 传 token，不要放 URL 或环境变量
- [2026-05-29] raw.githubusercontent.com 必须走代理（7890），github.com 和 api.github.com 直连即可
- [2026-05-29] 用 `hermes config set` 修改配置，不要直接写 config.yaml
- [2026-05-29] 用 `delegate_task` 并行派发独立任务，效率 x3
- [2026-05-29] 用 `patch` 编辑文件，不要用 sed/awk
- [2026-05-29] 用 `search_files` 搜索，不要用 grep/rg
- [2026-05-29] Wiki 和 Obsidian 共用目录（WIKI_PATH = Obsidian Vault）→ wikilinks 双向互通

### ❌ 不要做的
- [2026-05-29] 飞轮笔记只用 6 个 frontmatter 字段，不要混入 SCHEMA.md 的 type/confidence/sources
- [2026-05-29] 不要用 `echo "ghp_xxx" > file` 传 token — shell 会遮蔽为字面量 ***
- [2026-05-29] Windows 下不要用 `python3` — 指向 Windows Store 存根，用 `python`
- [2026-05-29] git push 不要走代理 — Clash 阻断 api.github.com (403)
- [2026-05-29] 不要尝试自动化 `hermes fallback add` — 它是交互式的，只能用户手动
- [2026-05-29] 不要试图直接读写 config.yaml 或 .env — 会被拦截
- [2026-05-29] 不要用 `execute_code` 的 terminal 执行长脚本 — 容易超时
- [2026-05-29] 不要跳过审核直接汇报 — commander 模式的三关审核必须走
- [2026-05-29] 不要反复重试 git push — 两次失败立刻换方案（API 或 GIT_ASKPASS）
- [2026-05-29] 不要在 execute_code 中用 token 做 GitHub API 调用 — token 被截断，返回 401
- [2026-05-31] memory 删除前必须先确认 old_text 确实存在于该条目中 — 批量盲删连错 7 次浪费 30K tokens
- [2026-05-31] 不要对 gateway 做破坏性操作（kill/restart）而不先确认 — 用户看不到你在干什么
- [2026-05-31] 微信消息限流根因是频率不是长度 — 1643 chars 单条过，785 chars 在密集 tool call 后被限流

### ✅ 应该做的
- [2026-06-12] 重启网关后必须重新检查优化参数是否丢失（`threshold_pct` 回到 10%、`child_timeout` 回到 600）
- [2026-06-12] SOUL.md 写入后必须 `hermes config set personality SOUL.md` 才能生效
- [2026-06-12] CC (Claude Code) 通过 DeepSeek Anthropic 兼容 API 使用，配置 6 个环境变量 + CLAUDE.md 职责文件
- [2026-06-12] 每次多步骤任务结尾必须有 ## ✅ 小结 + Token 消耗行
- [2026-06-12] 方案开头写"魏松山大人" + 方案总结 + 预估 token/费用，用 clarify 确认框等确认后执行
- [2026-06-12] 当输入"魏松山"时 — 说明丢了规则，读飞轮知识库修正自己并继续
- [2026-06-12] 多步骤任务必须有 ## ✅ 小结 + Token 消耗行
- [2026-06-12] 结论开头写"魏松山大人" + 方案总结 + 预估消耗
- [2026-06-12] 输入"魏松山"= 丢规则触发词，读飞轮库修正自己

## 架构决策

### 复合优于单一
- 指挥官（Hermes）+ 执行层（cc+reasonix）+ 知识层（wiki+obsidian）> 单一 agent 全包
- 优点：各司其职、token 分散、出问题好定位

### 技能组合 > 技能堆叠
- project-commander 作为框架，claude-code/reasonix/obsidian/llm-wiki 作为插件
- 不要在一个技能里塞所有逻辑

### 微信通信铁律（2026-05-31 实战教训）
- 分片间隔 10s / 重试 1 次 / 重试间隔 10s（源码实际 ×3 = 30s）
- 配置位置：`platforms.weixin.extra.send_chunk_delay_seconds` / `send_chunk_retries` / `send_chunk_retry_delay_seconds`
- Hermes v0.15.1 无熔断器（GitHub #26828 P1 open），限流窗口分钟级，密集重试必触发 OOM
- 自限单条 ≤500 chars，长任务结果聚合一条汇报不逐条推送
- 每次回复结尾必带 `🤖 模型 | token消耗`

## 待验证的假设
- [ ] cron 定期做 wiki lint 能否自动发现知识盲区？
- [ ] cc 往 wiki 归档代码变更摘要，能否让跨会话理解更快？
