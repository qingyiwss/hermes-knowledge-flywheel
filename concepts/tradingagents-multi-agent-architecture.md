---
id: 20260529-tradingagents
title: TradingAgents 多智能体交易架构拆解
tags: [skill-learning, automation, agent-upgrade, ai-model, strategy]
source_url: https://github.com/TauricResearch/TradingAgents
date_created: 2026-05-29
last_updated: 2026-05-29
---

# TradingAgents 多智能体交易架构拆解

## 🎯 核心痛点与应用场景

> TradingAgents 模拟真实交易公司的多角色协作，用多智能体辩论取代单一模型决策。对 Hermes 能力提升：将 Reasonix 从单路径分析升级为辩论式决策，降低模型偏见；引入交易记忆闭环让系统从历史错误中自我修正。

## 🛠️ 底层原理解析

- **核心逻辑描述：** 基于 LangGraph 构建有向工作流，9 个专业 Agent 按顺序协作：4 个分析师采集数据 → Bull/Bear 研究员辩论 → 研究经理综合 → 交易员出方案 → 激进/中立/保守三方风控辩论 → 投资经理最终五档决策。全程双 LLM 策略（廉价模型做扫描，昂贵模型做决策），带追加式记忆日志。

- **关键代码段/机制：**

```python
# 1. 辩论循环 — Bull/Bear 互相质疑直到收敛
workflow.add_conditional_edges(
    "Bull Researcher",
    should_continue_debate,  # 轮次未达上限则切到对方
    {"Bear Researcher": "Bear Researcher", "Research Manager": "Research Manager"}
)

# 2. 交易记忆 — pending→反射→resolved 闭环
class TradingMemoryLog:
    def get_past_context(self, ticker, n_same=5, n_cross=3):
        """注入历史教训到未来 Prompt：同标的最近 5 条 + 跨标的 3 条"""
        # 反射 Prompt（2-4 句精炼）：
        # "方向对吗？哪个假设成立/失败？一条具体教训。"

# 3. 双 LLM 策略 — 省钱干重活
self.deep_thinking_llm  = client.get_llm(model="gpt-5.4")      # 经理用
self.quick_thinking_llm = client.get_llm(model="gpt-5.4-mini") # 分析师用

# 4. 结构化输出 — 五档评级，确定性解析
# Portfolio Manager → PortfolioDecision → **Rating**: Buy/Overweight/Hold/Underweight/Sell
# SignalProcessor.process_signal() 用正则解析，不调 LLM

# 5. 配置覆盖 — 一行映射表搞定环境变量
_ENV_OVERRIDES = {
    "TRADINGAGENTS_LLM_PROVIDER": "llm_provider",
    "TRADINGAGENTS_DEEP_THINK_LLM": "deep_think_llm",
}
```

## 🔄 Hermes 进化映射 (Integration Roadmap)

- **关联现有技能：** [[ai-commander-system]], [[agent-reach-internet]], [[harness-engineering]]
- **改造方案：** 需要修改的核心模块和方向：

| 特性 | 改造模块 | 具体方向 |
|---|---|---|
| 辩论机制 | Reasonix 回测引擎 | 并行跑 bullish/bearish 两套参数，差异超阈值触发深度分析 |
| 交易记忆 | 新建 `trades/memory.md` | 每次回测后自动追加 pending → 下次回测注入 past_context |
| 双 LLM | `analyze.py` | 数据采集阶段用 flash，最终策略决策用 pro |
| 五档评级 | 决策输出层 | 当前二值（买/不买）→ Buy/Overweight/Hold/Underweight/Sell |
| 配置覆盖 | `config.py` | `_ENV_OVERRIDES` 映射表模式，类型自动推断 |
