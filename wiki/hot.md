# Hot Cache — 最新上下文
> 更新: 2026-06-12 · Wiki: 54篇 · 全面优化已执行

## 最近事件
- 🔧 **全面自我优化** — 7 项优化全部落地（详见下方）
- 📖 **Hermes v0.16 文档已学习** — DDGS / per-capability / checkpoints / Tool Gateway
- 🔍 **搜索升级** — DDGS (DuckDuckGo) 后端已配置，免费无 Key
- 🆕 **CC (Claude Code)** — v2.1.175，DeepSeek 兼容 API 驱动

## 生效的优化配置
- 🔍 `web.search_backend: ddgs` — 免费高质量搜索
- 📄 `auxiliary.web_extract.model: deepseek-v4-flash` — 摘要用便宜模型省费用
- ⏱️ `auxiliary.web_extract.timeout: 600` — 大页面不超时
- 🗜️ `compression.threshold: 0.45` — 更早触发压缩
- 🗜️ `compression.protect_last_n: 15` — 更激进压缩
- 💾 `checkpoints.enabled: true` — 防误改回滚
- 💾 `checkpoints.max_snapshots: 10` — 保留最近 10 个快照
- 🧠 `personality: SOUL.md` — 效率导向 persona 生效

## 底层规则
- 📋 方案: "魏松山大人" + 方案+预估 → clarify确认 → 执行
- 🔚 结尾: ## ✅ 小结 + Token 消耗行
- 🚨 "魏松山"= 丢规则触发词
- 🔄 飞轮后推库
