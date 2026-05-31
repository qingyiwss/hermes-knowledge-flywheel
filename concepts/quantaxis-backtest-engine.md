---
id: 20260529-quantaxis
title: QUANTAXIS 事件驱动回测引擎剖析
tags: [skill-learning, automation, agent-upgrade, re-capability]
source_url: https://github.com/yutiansut/QUANTAXIS
date_created: 2026-05-29
updated: 2026-05-29
last_updated: 2026-05-29
---

# QUANTAXIS 事件驱动回测引擎剖析

## 🎯 核心痛点与应用场景

> QUANTAXIS (⭐8.4K) 是国内最成熟的量化研究平台之一，提供从数据采集到回测的全链路方案。对 Reasonix 的提升：将当前简单的历史回测升级为**事件驱动 + 多因子复合择时 + 专业绩效归因**的完整评估体系，让 re 的决策质量从"能跑"提升到"可信赖"。

## 🛠️ 底层原理解析

- **核心逻辑描述：** 事件驱动架构按时间序列逐 bar 推进 — MarketEvent 触发 `on_bar()` → 策略计算信号 → Broker 模拟撮合 → Account 更新持仓资金。支持日线/分钟/Tick 多粒度，内置滑点、佣金、印花税等真实约束。多因子模块可叠加 **PE/PB/ROE/动量** 等多指标复合打分，Alpha 因子库支持自定义表达式。回测完成后一键输出绩效报告：夏普比率、最大回撤、Calmar、年化收益、胜率、盈亏比。

- **关键代码段/机制：**

```python
# 1. 事件驱动主循环 — 逐 bar 推进
class QA_Backtest:
    def run(self):
        for bar in self.market_data:
            event = QA_Worker(bar).query()        # MarketEvent
            signal = self.strategy.on_bar(event)  # 策略计算
            if signal:
                order = self.broker.match(signal) # 模拟撮合
                self.account.update(order)        # 资金/持仓更新

# 2. 多因子复合择时 — PE/PB/动量 加权叠加
factor_alpha = (
    QA_factor_pe(ts_code='000001.SZ') * 0.4 +
    QA_factor_pb(ts_code='000001.SZ') * 0.3 +
    QA_factor_momentum(ts_code='000001.SZ', window=20) * 0.3
)

# 3. 绩效归因 — 五维指标一键输出
analysis = QA_AccountAnalysis(account)
# → sharpe_ratio / max_drawdown / calmar / win_rate / profit_loss_ratio

# 4. 真实约束 + 多粒度配置
QA_backtest_strategy(
    frequency='1min',       # 1min / day / tick
    slippage=0.001,         # 滑点 0.1%
    commission=0.0003,      # 佣金 万三
    stamp_duty=0.001        # 印花税 千一
)
```

## 🔄 Hermes 进化映射 (Integration Roadmap)

- **关联现有技能：** [[tradingagents-multi-agent-architecture]]
- **改造方案：** 需要修改的核心模块和方向：

| 特性 | 改造模块 | 具体方向 |
|---|---|---|
| 事件驱动回测 | Reasonix 回测引擎 | for-loop 逐日计算 → Event-Driven 架构，支持 on_bar/on_tick 回调 |
| 多因子择时 | 策略评估模块 | 引入 PE/PB/ROE/动量 多指标加权打分，替代单一条件判断 |
| 绩效归因 | 评估输出层 | 仅输出收益 → 增加夏普/最大回撤/Calmar/胜率/盈亏比五维报告 |
| 真实约束 | 模拟撮合 | 增加滑点、佣金、印花税配置，回测结果更接近实盘 |
| 多粒度回测 | 数据引擎 | 支持 1min/5min/day/tick 多频率切换，覆盖短线/长线策略 |
