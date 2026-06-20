# Hot Cache — 最新上下文
> 更新: 2026-06-20 · Wiki: 62篇 · MiMo 模型时代

## 最近事件
- 🔄 **模型切换** — DeepSeek V4 Pro → MiMo-V2.5-Pro（小米），全栈迁移（Hermes + CC + 子代理）
- 📊 **飞轮#1-4** — Token消耗+缓存命中+执行效率+工具链+最佳实践（六篇 Wiki）
- 🌐 **独立站上线** — qingyiwss.github.io/saudi-trade-site（英阿双语，GEO 优化，55/57 Q&A FAQ）
- 🔧 **Loop Engineering** — hermes-cc-worktree.sh + hermes-cc-loop.sh 补齐
- 📱 **外贸渠道调研** — WhatsApp 中东回复率 50%+，多渠道叠加 +287%

## MiMo 模型配置
- 主模型：mimo-v2.5-pro（xiaomi, token-plan-cn.xiaomimimo.com）
- 子代理/辅助：mimo-v2-flash
- 费用：输入 ¥3/百万（缓存命中 ¥0.025），输出 ¥6/百万
- Claude Code 设置：~/.claude/settings.json 已同步
- 智能体任务能力 #5/92，编程 #8/92
- 简洁度 #4/92（输出比平均少 13%）

## 生效的优化配置
- 📄 `auxiliary.web_extract.model: mimo-v2-flash` — 摘要省 75%
- 🗜️ `LCM_CONTEXT_THRESHOLD=0.20` — 200K 触发压缩
- 🔍 `tools.tool_search.threshold_pct: 3` — 减少工具注入
- ⏱️ `delegation.child_timeout_seconds: 300` — 子代理 5 分钟超时
- 🧠 `personality: SOUL.md` — 效率导向
- 💰 成本监控阈值：日均 >¥20 预警，缓存命中率 <50% 预警

## 底层规则
- 📋 方案: "魏松山大人" + 预估 → clarify → 执行 → ## ✅
- 🚨 "魏松山"= 丢规则触发词
- 🔄 飞轮后推库（growth-log + lessons-learned + hot.md）
- 🌐 翻译铁律：能翻译的尽量翻译
- 💻 CC 出错退回 CC 修，Hermes 不越位
- ⚠️ settings.json 优先级高于 shell 环境变量
- 🔧 工具选择：专用工具 > terminal > browser

## Wiki 索引（飞轮系列）
- `token-optimization.md` — Token 消耗优化七大策略
- `cache-hit-optimization.md` — 缓存命中三断点架构
- `execution-efficiency.md` — 执行效率六大策略
- `mimo-v25pro-optimization.md` — MiMo 模型特有优化
- `cost-monitoring.md` — 成本监控与预警
- `toolchain-optimization.md` — 工具链优化实战
- `best-practices-summary.md` — 速查表+实施优先级+预期收益
