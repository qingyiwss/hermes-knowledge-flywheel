---
title: "NΞXUS 双引擎多智能体方案"
aliases: [Hermes + Claude Code 协作架构, 多智能体系统部署]
created: 2026-06-01
tags: [hermes-agent, claude-code, multi-agent, architecture, gstack]
status: active
---

# NΞXUS 双引擎多智能体方案

> 基于「Hermes Agent 7个等级」视频精华 + Hermes Agent + Claude Code + gstack 的真实能力，为 macOS 10.15.7 Catalina 环境定制的实战方案。

## 一、核心理念：双引擎分工

视频诊断「30天崩溃陷阱」的根因是**单一智能体共享记忆池污染**。NΞXUS 的解法不是造一个全能神，而是让两个引擎各司其职：

```
┌─────────────────────────────────────────────┐
│              NΞXUS 双引擎架构                 │
│                                             │
│   ┌──────────────┐    ┌──────────────┐      │
│   │  Hermes Agent │◄──►│ Claude Code  │      │
│   │  (总指挥)     │    │  (代码工人)   │      │
│   │              │    │              │      │
│   │ • 任务分解    │    │ • 写代码      │      │
│   │ • 通信/运维   │    │ • 审查/测试   │      │
│   │ • 知识沉淀    │    │ • Git操作     │      │
│   │ • 子代理调度  │    │ • 格式化      │      │
│   │ • 微信交互    │    │              │      │
│   └──────┬───────┘    └──────┬───────┘      │
│          │                   │              │
│   ┌──────┴───────────────────┴──────┐       │
│   │         NΞXUS 知识库            │       │
│   │    ~/nexus-knowledge/ (48篇)    │       │
│   │    Hermes 写入  /  CC 只读      │       │
│   └─────────────────────────────────┘       │
└─────────────────────────────────────────────┘
```

**分工铁律（不可违反）：**

| 职责 | Hermes | Claude Code |
|------|:------:|:-----------:|
| 写代码 / 改代码 / 测试 / Git / 格式化 | ❌ | ✅ 唯一 |
| 代码审查（review/qa/cso） | ❌ | ✅ gstack |
| 部署发布（ship/land-and-deploy） | ❌ | ✅ gstack |
| 任务规划 / 需求分解 | ✅ 唯一 | 辅助 |
| 运维 / 系统配置 / 网络修复 | ✅ 唯一 | ❌ |
| 知识沉淀 / Wiki 编写 | ✅ 唯一 | ❌ |
| 子代理调度 / delegate_task | ✅ 唯一 | ❌ |
| 微信交互 / 用户通信 | ✅ 唯一 | ❌ |
| 读知识库辅助决策 | ✅ | ✅ 只读 |
| 研究搜索 / 数据分析 | ✅ 唯一 | ❌ |

## 二、通信协议：hermes-cc 桥梁

```
Hermes (微信/CLI)
    │
    │  ~/.local/bin/hermes-cc "任务描述"
    ▼
本地代理 :8787 (thinking:disabled 注入)
    │
    ▼
Claude Code -p 模式 (DeepSeek Anthropic API)
    │
    │  代码写入 ~/code/claudecode/
    │
    ▼
stdout → Hermes 读取结果
```

**启动代理：** `nohup python3 ~/.local/bin/cc-deepseek-proxy.py &`

**日常用法：** `~/.local/bin/hermes-cc "检查 src/auth.py 的安全问题，纯文本回复"`

**CC 回复格式：** `[CC] 纯文本` 前缀，每步附物证（文件路径/测试结果）。

## 三、视频六步蓝图 → NΞXUS 映射

### ❶ 云端环境

| 视频要求 | NΞXUS 现状 | 方案 |
|----------|-----------|------|
| 7×24 在线 | macOS 本地，可能休眠 | gateway launchctl KeepAlive 已启用 |
| 后台任务 | — | cronjob 调度器已内置 |
| 云端隔离 | — | 可选：腾讯云轻量服务器 + SSH backend |

**当前方案：** macOS 不关机 + gateway KeepAlive + cronjob 兜底。够用。

### ❷ 角色隔离（视频的 clone → Hermes 的 profile）

视频说的「clone 创建新角色，物理层面上下文隔离」在 Hermes 里就是 **profile 系统**。每个 profile 有独立的 skills/、memory/、sessions/：

```bash
# 研究员 profile（web+browser 工具集）
hermes profile create researcher --clone
# 在 config.yaml 中限制 toolsets: [web, search, browser, file]

# 编码协调员 profile（delegation+terminal 工具集）
hermes profile create orchestrator --clone
# toolsets: [terminal, file, delegation, skills, session_search]
```

**但当前不需要**——有 CC 做代码工人，Hermes 的 delegate_task 已经提供了子代理隔离。Profile 是第二步优化。

### ❸ 三人小队（视频的团队协作 → delegate_task + CC + gstack）

视频的经典三人设定映射到 NΞXUS：

```
视频角色          NΞXUS 实现           工具
─────────────────────────────────────────────
研究员            delegate_task          web, search, browser
（全网溯源）       (单子代理)

编码员            Claude Code            Bash, Edit, Write
（写代码）         (hermes-cc 调用)       通过 gstack 增强

评估员/协调员     Hermes Agent 本体      delegate_task, file,
（统筹审核）       本身                    skills, memory
```

**实战流程：**

```
1. 用户：「帮我分析倚天2觉醒的封号机制，然后写个检测脚本」

2. Hermes（评估员）分解任务：
   ├── 子任务A → delegate_task(researcher): 「搜倚天2 2024-2026年私服反作弊」
   └── 子任务B → 等研究员返回后，hermes-cc: 「基于以下研究写检测脚本...」

3. 研究员（delegate_task）返回研究报告 → Hermes 验证 → CC 写代码

4. CC 写完后 → Hermes 调 CC /review 审查 → 通过 → 返回用户
```

**关键规则：** CC 永远不直接和用户对话。Hermes 是唯一用户界面。

### ❹ 交接合同（视频的格式约束 → SKILL.md + CLAUDE.md）

视频强调「强制交接合同，铁面无私质检员」。在 NΞXUS 里：

**Hermes → CC 的交接合同：** CLAUDE.md 定义了：
- CC 只写代码不改知识库
- CC 回复格式 `[CC] 纯文本`
- CC 每步附物证
- CC 的任务通过 hermes-cc 传入

**Hermes → delegate_task 的交接合同：** SKILL.md 定义了：
- 触发条件
- 输入格式
- 输出格式
- 验证步骤

**代码审查的交接合同：** gstack /review → 输出 bugs + security + style 三项

### ❺ 三级异常恢复

视频的三级机制在 NΞXUS 的落地：

| 级别 | 视频描述 | NΞXUS 实现 |
|------|---------|-----------|
| 一级 | 自动重试 | delegate_task 失败 → 换 toolset 重试 |
| 二级 | 策略切换 | web_search 被墙 → browser_snapshot；GitHub API 限流 → browser_navigate |
| 三级 | 任务拆解 | 大任务 → writing-plans → delegate_task 分包 → subagent-driven-development 两阶段审查 |

**当前 Hermes 已在实践中自然使用二级切换**（网络修复时自动从 terminal 切换到 browser），需要规范化为显式流程。

### ❻ 系统优化

| 视频指标 | NΞXUS 当前 | 行动 |
|----------|-----------|------|
| 15% 记忆红线 | memory 23% / user 26% | ✅ 健康，暂不需清理 |
| 任务错峰 | 无 | 如加 cronjob 需错开>30分钟 |
| 版本控制 | CLAUDE.md 已管控 | ✅ |
| 定期审计 | 无 | 建议每月检查 memory 和 profile 一致性 |

## 四、gstack 40+ 技能：三阶段覆盖

gstack 是 CC 的武器库，覆盖软件开发全生命周期：

```
规划阶段                    实施阶段                    发布阶段
/office-hours ─┐          /review ────┐              /ship ──────┐
/autoplan ─────┤ 产出Spec  /codex ─────┤ 写代码+审查  /land-and-deploy 部署
/spec ─────────┘          /qa ────────┤              /canary ────┘ 监控
                          /investigate 调试         /retro ───── 回顾
                          /cso ───────┘ 安全审计
```

**安全意识：**
- `/careful` — 破坏性操作警告
- `/freeze` — 锁定目录禁止编辑
- `/guard` — careful + freeze 同时启用
- `/cso` — OWASP Top 10 + STRIDE 安全审计

## 五、限制与现实约束

### macOS 10.15 Catalina 的硬限制

| 能力 | 状态 | 原因 |
|------|------|------|
| Claude Code | 0.2.9 可用 | 1.0+ 需要 macOS 13+ |
| computer_use | ❌ 不可用 | 需要 ScreenCaptureKit (macOS 12+) |
| tmux | 可安装但困难 | Homebrew Tier 3 |
| CC -p 模式工具执行 | ✅ 已验证 | 需 `~/.claude.json` 设 allowedTools |
| CC thinking blocks | 🔧 需代理 | 代理注入 thinking:disabled |

**这是最重要的现实约束。** Catalina 上所有方案都必须在"不用 computer_use 和 tmux"的前提下设计。

### 解决方案：hermes-cc 代理通道

```
[已构建的三组件]

cc-deepseek-proxy.py    ~/.local/bin/   → 本地代理 :8787，注入 thinking:disabled
hermes-cc               ~/.local/bin/   → 绕行密钥掩码 + 调 CC -p 模式
start-claude            ~/.local/bin/   → 交互式 CC，自动启动代理
```

## 六、实战案例：倚天2脚本适配

以下是用这套方案处理「倚天2觉醒脚本适配」的真实流程：

```
Phase 1 — 研究（Hermes 本体）
  ├── terminal: git clone 三个脚本仓库
  ├── browser_navigate: 搜索 GitHub 高星仓库
  ├── read_file: 逐文件源码审计
  └── skill_manage: 沉淀为 3 个 SKILL.md

Phase 2 — 编码（Claude Code）
  ├── hermes-cc "基于 nohachi/Mt2-Stone-Farm-Bot 的 config/maps/，
  │              将坐标替换为倚天2觉醒地图坐标，修改 stones/ 模板图"
  ├── CC 读取知识库中的 nohachi SKILL.md
  ├── CC 执行修改 → git commit
  └── hermes-cc "/review 检查修改"

Phase 3 — 交付（Hermes 本体）
  ├── terminal: 运行 git diff 验证改动
  ├── send_message: 通过微信交付结果
  └── memory: 记录「倚天2觉醒脚本已适配」
```

## 七、日常操作速查

### Hermes 调 CC 写代码

```bash
# 小任务
~/.local/bin/hermes-cc "在 ~/code/claudecode/ 创建一个 hello.py，打印 Hello World，加类型注解"

# 代码审查
~/.local/bin/hermes-cc "/review 检查 src/auth.py"

# 安全审计
~/.local/bin/hermes-cc "/cso 审计整个项目"

# 自动规划+实现
~/.local/bin/hermes-cc "/autoplan 用户认证系统 然后 /spec 然后实现"
```

### Hermes 自主处理

```
# 研究任务（不用 CC）
delegate_task(goal="搜索倚天2 2024-2026 反作弊机制")
web_search("倚天2私服 封号检测")
browser_navigate("https://epvp.com/...")

# 知识沉淀
skill_manage(action='create', ...)
write_file(path="~/nexus-knowledge/.../xxx.md", ...)

# 运维
terminal("brew update && brew upgrade")
cronjob(action='create', schedule='0 */6 * * *', ...)
```

## 八、启动检查清单

每次重要任务前，确认以下四项：

```
□ 代理在线：curl -s --max-time 3 http://127.0.0.1:8787/
□ CC 可用：which claude && claude --version  # 0.2.9
□ 代理连通：export HTTP_PROXY=http://127.0.0.1:7890 ...
□ CC config：cat ~/.claude.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('autoUpdaterStatus','?'))"
  # 必须为 disabled（防止 Catalina 被静默升级到 2.x 炸掉）
```

## 九、对比总结

| 维度 | 视频推荐 | NΞXUS 方案 | 成熟度 |
|------|---------|-----------|--------|
| 角色隔离 | clone 命令 | profile + delegate_task | ✅ 可用 |
| 三人团队 | 手动分配 | delegate_task(研究员) + CC(编码员) + Hermes(评估员) | ✅ 已验证 |
| 交接合同 | 手动约定 | SKILL.md + CLAUDE.md | ✅ 已落地 |
| 云端环境 | 腾讯云 | 本地 macOS + gateway KeepAlive | ⚠️ 基本够用 |
| 异常恢复 | 三级机制 | delegate重试 + 工具切换 + task拆分 | ✅ 已自然使用 |
| 记忆监控 | 15% 红线 | 手动检查 memory 使用率 | ⚠️ 无自动告警 |
| 代码执行 | 沙盒 | CC -p 模式 + gstack 40+ 技能 | ✅ 生产可用 |
| 桌面控制 | — | ❌ Catalina 永久不可用 | ❌ 硬限制 |

## 十、下一步

1. **立即：** 启动代理 `nohup python3 ~/.local/bin/cc-deepseek-proxy.py &`
2. **本周：** 测试一次完整的「研究→编码→审查」流程
3. **按需：** 根据实际使用频率决定是否创建专用 profile

---

*基于 Hermes Agent + Claude Code 0.2.9 + gstack + NΞXUS 知识库 48 篇 Wiki。*  
*协作协议详见 `~/nexus-knowledge/concepts/nexus-dual-engine.md`*
