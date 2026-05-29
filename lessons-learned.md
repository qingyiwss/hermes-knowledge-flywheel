# 经验教训

> 犯错即记，好做法即存。只追加不删除。
> 这是系统的"抗退化机制"。

## 工具和技巧

### ✅ 应该做的
- [2026-05-29] 用 `hermes config set` 修改配置，不要直接写 config.yaml
- [2026-05-29] 用 `delegate_task` 并行派发独立任务，效率 x3
- [2026-05-29] 用 `patch` 编辑文件，不要用 sed/awk
- [2026-05-29] 用 `search_files` 搜索，不要用 grep/rg
- [2026-05-29] Wiki 和 Obsidian 共用目录（WIKI_PATH = Obsidian Vault）→ wikilinks 双向互通

### ❌ 不要做的
- [2026-05-29] 不要尝试自动化 `hermes fallback add` — 它是交互式的，只能用户手动
- [2026-05-29] 不要试图直接读写 config.yaml 或 .env — 会被拦截
- [2026-05-29] 不要用 `execute_code` 的 terminal 执行长脚本 — 容易超时
- [2026-05-29] 不要跳过审核直接汇报 — commander 模式的三关审核必须走

## 架构决策

### 复合优于单一
- 指挥官（Hermes）+ 执行层（cc+reasonix）+ 知识层（wiki+obsidian）> 单一 agent 全包
- 优点：各司其职、token 分散、出问题好定位

### 技能组合 > 技能堆叠
- project-commander 作为框架，claude-code/reasonix/obsidian/llm-wiki 作为插件
- 不要在一个技能里塞所有逻辑

## 待验证的假设
- [ ] cron 定期做 wiki lint 能否自动发现知识盲区？
- [ ] cc 往 wiki 归档代码变更摘要，能否让跨会话理解更快？
