# Hot Cache — 最新上下文
> 更新: 2026-06-20 · Wiki: 64篇 · MiMo 模型时代

## 最近事件
- 🔄 **模型切换** — DeepSeek V4 Pro → MiMo-V2.5-Pro（小米），全栈迁移
- 📊 **飞轮#1-5** — Token消耗+缓存命中+执行效率+工具链+最佳实践+验证（8篇新 Wiki）
- 🏗️ **飞轮库大修** — concepts/ 54篇全量迁入 wiki/，BOOTSTRAP 现代化，index.md 重建
- 📚 **CC 能力升级** — Supabase+Next.js 指南，CLAUDE.md 三阶段工作流
- 🎓 **CC 官方指南学习** — CLAUDE.md 层级结构+自然语言指令+工具集成
- 🌐 **独立站上线** — qingyiwss.github.io/saudi-trade-site（英阿双语，GEO 优化）

## 模型配置
| 角色 | 模型 | 提供商 |
|------|------|--------|
| Hermes 主模型 | mimo-v2.5-pro | xiaomi |
| CC 主模型 | mimo-v2.5-pro | xiaomi (Anthropic 兼容) |
| CC 子代理 | mimo-v2-flash | xiaomi |
| 辅助模型 | mimo-v2-flash | xiaomi |

**价格**：Pro 输入 ¥3/百万（缓存 ¥0.025），Flash 输入 ¥0.8/百万（缓存 ¥0.02）

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
- ⚠️ settings.json 优先级高于 shell 环境变量
- 🔧 工具选择：专用工具 > terminal > browser
- 📊 每日验证：缓存命中率+Token消耗+成本

## CC 能力指南
- `~/.claude/CLAUDE.md` — 全局指南（144 行，含三阶段工作流）
- `CLAUDE-supabase.md` — Supabase 全栈操作
- `CLAUDE-nextjs.md` — Next.js App Router 深度指南
- `wiki/claude-code-best-practices.md` — CC 最佳实践 Wiki

## 飞轮库结构
- **wiki/**: 64 篇（63 原有 + 1 新增 CC 最佳实践）
- **growth-log.md**: 进化日志
- **lessons-learned.md**: 经验教训（+3 条新增）
- **index.md**: 分类目录（15 个分类）
- **BOOTSTRAP.md**: v2.0 已现代化（Linux + MiMo）
