---
id: 20260529-litellm
title: LiteLLM AI 网关成本优化拆解
tags: [skill-learning, automation, agent-upgrade, token-optimization]
source_url: https://github.com/BerriAI/litellm
date_created: 2026-05-29
last_updated: 2026-05-29
---

# LiteLLM AI 网关成本优化拆解

## 🎯 核心痛点与应用场景

> LiteLLM 统一 100+ LLM 的 OpenAI 格式调用，内置自动路由、负载均衡、成本追踪、预算控制。Stripe/Netflix 都在用。对 Hermes 的直接价值：实现按复杂度自动路由到不同成本模型（如 flash 做简单任务，pro 做复杂决策），并追踪每次调用的实际花费。

## 🛠️ 底层原理解析

- **核心逻辑描述：** 统一 API 网关 → Router 根据配置（成本/延迟/可用性）选择模型 → 自动 fallback → 记录每次调用的 token 消耗和费用 → 预算告警。P95 延迟 8ms @ 1K RPS。

- **关键机制：**

```python
# 1. 统一调用 — 任意模型，OpenAI 格式
from litellm import completion
response = completion(
    model="deepseek/deepseek-chat",  # 任意 provider:model
    messages=[{"role": "user", "content": "Hello"}]
)

# 2. 自动路由 — 按成本/延迟选择
from litellm import Router
router = Router(model_list=[
    {"model_name": "gpt-4", "litellm_params": {"model": "openai/gpt-4"}},
    {"model_name": "claude-3", "litellm_params": {"model": "anthropic/claude-3"}},
])
router.set_model_list(model_list)  # 动态更新模型列表
response = router.completion(model="best-model", messages=[...])
# 自动选最便宜/最快的，失败自动 fallback

# 3. 成本追踪 — 每次调用的实际花费
# response._hidden_params 包含:
# {"response_cost": 0.0023, "token_usage": {"prompt": 150, "completion": 50}}

# 4. 预算控制 — 超限自动拒绝
router.set_budget(100.0)  # $100 月预算
# 超预算 → 返回 429，不浪费钱
```

## 🔄 Hermes 进化映射 (Integration Roadmap)

- **关联现有技能：** [[ai-commander-system]], [[model-router]]

| 应用场景 | 改造方案 | 预期收益 |
|---|---|---|
| 模型自动路由 | 简单命令用 flash，复杂分析用 pro | ~50% 成本 |
| 成本追踪面板 | 每次对话末尾显示本次消耗和累计费用 | 透明可控 |
| 预算硬限制 | 月预算告警 + 自动降级到便宜模型 | 不超支 |
| Fallback 链 | pro 不可用 → 自动切 flash → 再切 openrouter | 零宕机 |
