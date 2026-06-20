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
- [2026-06-12] 搜索后端 DDGS (DuckDuckGo) 配置于 `web.search_backend: ddgs`，无需 API Key，`pip install ddgs` 即可
- [2026-06-12] Hermes web 搜索支持 per-capability 配置：`web.search_backend` 和 `web.extract_backend` 可独立设置不同的后端
- [2026-06-12] web_extract 辅助模型可节省摘要费用：`auxiliary.web_extract.model = deepseek-v4-flash`
- [2026-06-12] checkpoints 开启后可用 `/rollback` 回滚文件快照
- [2026-06-12] compression.protect_last_n 控制压缩保留的倒数消息数，15 比 20 更激进
- [2026-06-12] 辅助模型切换方案：compression/title_generation/curator/approval 切到 deepseek-v4-flash，省 ~85% 辅助任务费用。这些任务不需要深度推理，flash 模型性价比最高
- [2026-06-12] 模型切换三方案：fallback_providers（自动降级）、claude -m（手动切换）、/model（会话级切换）。Auxiliary slot 可独立配 cheap model 省费用
- [2026-06-12] 搜索后端配置：`web.search_backend = google`。这台服务器（LAX）Google 直连 245ms，比 DDGS/Bing 更快，中文搜索质量好。`search_backend` 是单值配置，不支持优先级列表。
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

## Token 消耗 + 缓存 + 效率 (2026-06-20)

### L1: Claude Code settings.json 覆盖 shell 环境变量
- **症状**：hermes-cc.sh 已更新为 MiMo，但 CC 实际运行仍是 DeepSeek
- **根因**：~/.claude/settings.json 的 env 配置优先级高于 shell export
- **修复**：切换模型时必须同时更新 settings.json + hermes-cc.sh + worktree/loop 脚本
- **验证**：CC 返回 JSON 中 modelUsage 字段确认实际使用模型

### L2: MiMo 缓存价格是杀手级优势
- **数据**：缓存命中 ¥0.025/百万 vs 未命中 ¥3/百万（120 倍差距）
- **实践**：保持系统提示和工具定义稳定，最大化前缀缓存命中
- **注意**：LCM 压缩会改变历史内容，需开启 CACHE_FRIENDLY_CONDENSATION

### L3: no_agent Cron 是最高效的监控模式
- **数据**：零 Token + <5 秒延迟（vs 智能体模式 30-60 秒）
- **适用**：数据采集、参数巡检、价格追踪、定时报告
- **限制**：需要推理/判断的任务仍需智能体模式

### L4: CC 任务描述精度直接决定执行效率
- **反面**："优化一下" → CC 猜测 → 重做 → 浪费 2-3 轮
- **正面**：精确描述（文件名/段落/CSS 类/数据结构）→ 一步到位
- **经验**：任务描述多花 30 秒写精确，省 2-3 分钟的重做


### L5: MiMo 推理模式消耗隐藏 Token
- **现象**：表面输出 200 Token，实际思考消耗 500-1000 Token
- **影响**：简单任务总消耗可能翻倍
- **优化**：简单任务用 mimo-v2-flash（非推理），复杂任务才用 Pro
- **验证**：API 响应中 usage.total_tokens 包含思考 Token

### L6: MiMo 简洁度是天然优势但需注意
- **数据**：#4/92 最简洁模型，输出比平均少 13%
- **优势**：输出 Token 费用自然降低
- **风险**：过度简洁可能遗漏关键细节
- **平衡**：报告类任务在 prompt 中指定详细程度

### L7: 缓存命中率是成本优化的最大单一杠杆
- **数据**：缓存命中 $0.004 vs 未命中 $0.435（109 倍差距）
- **目标**：>70% 命中率（当前 ProjectDiscovery 实战验证可达 84%）
- **实践**：系统提示稳定 + 工具定义固定 + session-sticky routing

