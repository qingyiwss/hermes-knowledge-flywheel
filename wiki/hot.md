# Hot Cache — 最新上下文
> 更新: 2026-06-13 · Wiki: 55篇 · 量化框架已安装

## 最近事件
- 📊 **量化工作区搭建** — Freqtrade v2026.5.1 + NautilusTrader 双框架
- 🔧 **全面自我优化 7 项** — web_extract省钱、压缩更激进、checkpoints防误改
- 🔍 **DDGS 搜索配置** — 免费高质量搜索，中英文均优
- 🆕 **CC (Claude Code)** — v2.1.175，DeepSeek API 驱动
- 🤖 **主模型** — deepseek-v4-pro（已切换）

## 量化工作区
- 框架：Freqtrade (交易) + NautilusTrader (回测)
- 路径：/root/code/quant/
- 策略：NostalgiaForInfinityX（社区最成熟，38,977行）+ SampleStrategy
- 市场：加密货币（OKX/Binance）

## 生效的优化配置
- 🔍 `web.search_backend: ddgs` — 免费搜索
- 📄 `auxiliary.web_extract.model: deepseek-v4-flash` — 摘要省 85%
- 🗜️ `compression.threshold: 0.45 / protect_last_n: 15` — 激进压缩
- 💾 `checkpoints.enabled: true` — /rollback 防误改
- 🧠 `personality: SOUL.md` — 效率导向

## 底层规则
- 📋 方案: "魏松山大人" + 预估 → clarify → 执行 → ## ✅
- 🚨 "魏松山"= 丢规则触发词
- 🔄 飞轮后推库
