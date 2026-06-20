# Hot Cache — 最新上下文
> 更新: 2026-06-20 · Wiki: 58篇 · MiMo 模型时代

## 最近事件
- 🔄 **模型切换** — DeepSeek V4 Pro → MiMo-V2.5-Pro（小米），全栈迁移（Hermes + CC + 子代理）
- 📊 **Token/缓存/效率飞轮#1** — 三篇 Wiki 创建，基于外部调研+实战数据
- 🌐 **独立站上线** — qingyiwss.github.io/saudi-trade-site（英阿双语，GEO 优化，55/57 Q&A FAQ）
- 🔧 **Loop Engineering** — hermes-cc-worktree.sh + hermes-cc-loop.sh 补齐
- 📱 **外贸渠道调研** — WhatsApp 中东回复率 50%+，多渠道叠加 +287%

## MiMo 模型配置
- 主模型：mimo-v2.5-pro（xiaomi, token-plan-cn.xiaomimimo.com）
- 子代理/辅助：mimo-v2-flash
- 费用：输入 ¥3/百万（缓存命中 ¥0.025），输出 ¥6/百万
- Claude Code 设置：~/.claude/settings.json 已同步

## 生效的优化配置
- 📄 `auxiliary.web_extract.model: mimo-v2-flash` — 摘要省 75%
- 🗜️ `LCM_CONTEXT_THRESHOLD=0.20` — 200K 触发压缩
- 🔍 `tools.tool_search.threshold_pct: 3` — 减少工具注入
- ⏱️ `delegation.child_timeout_seconds: 300` — 子代理 5 分钟超时
- 🧠 `personality: SOUL.md` — 效率导向

## 底层规则
- 📋 方案: "魏松山大人" + 预估 → clarify → 执行 → ## ✅
- 🚨 "魏松山"= 丢规则触发词
- 🔄 飞轮后推库（growth-log + lessons-learned + hot.md）
- 🌐 翻译铁律：能翻译的尽量翻译
- 💻 CC 出错退回 CC 修，Hermes 不越位

## Wiki 索引（最近新增）
- `token-optimization.md` — Token 消耗优化七大策略
- `cache-hit-optimization.md` — 缓存命中三断点架构
- `execution-efficiency.md` — 执行效率六大策略
