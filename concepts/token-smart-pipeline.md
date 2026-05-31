---
id: 20260529-token-smart-pipeline
title: Token Smart Pipeline — 三层优化引擎落地
tags: [skill-learning, automation, agent-upgrade, token-optimization, 自研]
date_created: 2026-05-29
updated: 2026-05-29
last_updated: 2026-05-29
---

# Token Smart Pipeline — 三层优化引擎落地

## 🎯 核心痛点与应用场景

> 将 LLMLingua 压缩、GPTCache 缓存、LiteLLM 路由三层理论方案落地为可运行的 Python pipeline。一次 `pipe.ask(prompt)` 自动经过 **压缩→缓存→路由** 三阶段，最小化 token 消耗和 API 费用。

## 🛠️ 底层原理解析

- **核心逻辑描述：** 三层级联处理。L1 用 LLMLingua-2 BERT 压缩 prompt（减少输入 token）；L2 用 SQLite 做精确匹配缓存（相同请求直接返回，零 API 调用）；L3 用关键词+长度启发式判定复杂度，自动路由 flash/pro。

```
用户请求
    ↓
[L1 压缩] LLMLingua-2 BERT → 移除低信息量 token
    ↓
[L2 缓存] SQLite MD5 匹配
    ├─ 命中 → 返回缓存（0 cost, <1ms）
    └─ 未命中 ↓
[L3 路由] 复杂度判定
    ├─ 含"分析/优化/调试" → deepseek-reasoner (pro)
    ├─ >300 字 → pro
    └─ 其余 → deepseek-chat (flash)
    ↓
存缓存 + 返回结果 + 成本追踪
```

- **关键机制：**

```python
from token_smart_pipeline import SmartPipeline

pipe = SmartPipeline(compress_rate=0.5, budget_monthly=50.0)

# 自动压缩→缓存→路由
result = pipe.ask("什么是 Python？")
print(result.text)          # LLM 回复
print(result.model_used)    # deepseek-flash
print(result.cost_usd)      # $0.000023
print(result.layer_used)    # "cache" | "llm"

# 第二次同样问题 → 缓存命中，零费用
result2 = pipe.ask("什么是 Python？")
# layer_used="cache", cost_usd=0

# 统计
print(pipe.stats())
# {"total_calls": 3, "cache_hits": 1, "cache_hit_rate": "33%", "total_cost": "$0.0001", ...}
```

## 🔄 Hermes 进化映射 (Integration Roadmap)

- **关联现有技能：** [[llmlingua-prompt-compression]], [[gptcache-semantic-cache]], [[litellm-ai-gateway]]

| 应用场景 | 改造方案 | 预期收益 |
|---|---|---|
| 飞轮扫描缓存 | 已扫描过的 repo 直接返回缓存笔记 | 省 ~30% API 调用 |
| 简单问题路由 | "你好" / "什么是X" → flash | 单次省 ~85% 费用 |
| 复杂分析路由 | 架构/调试/优化 → pro (reasoner) | 质量不降 |
| 预算硬限制 | 月预算 $50，超限自动降级 flash | 永不超支 |
| 成本面板 | 每次对话显示累计费用 | 透明可控 |

## ⚠️ 已知局限

- LLMLingua-2 对中文压缩效果较弱（压缩率仅 ~7%），后续可换 LongLLMLingua 或自研中文压缩方案
- 缓存为精确匹配（MD5），不支持语义相似匹配（GPTCache 初始化复杂，降级为 SQLite）
- 需手动设置 `DEEPSEEK_API_KEY` 环境变量

## 📂 代码位置

`D:\Reasonix\token_smart_pipeline.py`（372 行）
