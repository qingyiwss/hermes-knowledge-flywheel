---
id: 20260529-gptcache
title: GPTCache LLM 语义缓存拆解
tags: [skill-learning, automation, agent-upgrade, token-optimization]
source_url: https://github.com/zilliztech/GPTCache
date_created: 2026-05-29
updated: 2026-05-29
last_updated: 2026-05-29
---

# GPTCache LLM 语义缓存拆解

## 🎯 核心痛点与应用场景

> GPTCache 用语义相似度匹配缓存 LLM 响应。相似问题直接返回缓存，避免重复 API 调用。对 Hermes 的直接价值：飞轮扫描时的 API 查询、重复的代码搜索、相似的错误诊断都可以缓存，省 10x 成本、快 100x。

## 🛠️ 底层原理解析

- **核心逻辑描述：** 请求 → 嵌入向量 → 相似度搜索（余弦/欧氏）→ 命中则返回缓存 → 未命中则调 LLM → 存入缓存。支持多种嵌入后端（OpenAI/HuggingFace/本地）和存储后端（内存/Redis/SQLite/Milvus）。

- **关键机制：**

```python
# 核心 API — 两行接入
from gptcache import cache
from gptcache.adapter import openai

cache.init()  # 默认：内存存储 + OpenAI 嵌入
cache.set_openai_key()

# 之后正常调 OpenAI API，自动缓存
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is prompt caching?"}]
)
# 第二次相同/相似问题 → 直接返回缓存，不调 API

# 自定义配置：
cache.init(
    embedding_func=embedding_fn,  # HuggingFace 本地嵌入
    data_manager=data_manager,    # Redis 持久化存储
    similarity_threshold=0.8,     # 相似度阈值
    eviction_policy="LRU"         # 淘汰策略
)
```

## 🔄 Hermes 进化映射 (Integration Roadmap)

- **关联现有技能：** [[ai-commander-system]], knowledge-flywheel

| 应用场景 | 改造方案 | 预期节省 |
|---|---|---|
| 飞轮 API 查询 | 缓存 GitHub API 搜索结果 | ~80% API 调用 |
| 重复错误诊断 | 相似错误堆栈 → 直接复用之前的修复方案 | ~60% 诊断时间 |
| 代码搜索 | 相似代码搜索缓存结果 | ~50% 搜索 |
| Skill 文档查询 | 缓存 skill 加载和解读结果 | ~40% 冷启动 |
