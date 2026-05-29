---
id: 20260529-llmlingua
title: LLMLingua Prompt 压缩技术拆解
tags: [skill-learning, automation, agent-upgrade, token-optimization]
source_url: https://github.com/microsoft/LLMLingua
date_created: 2026-05-29
last_updated: 2026-05-29
---

# LLMLingua Prompt 压缩技术拆解

## 🎯 核心痛点与应用场景

> LLMLingua 用小型 LM（GPT2-small/Llama-7B）识别 prompt 中的非必要 token，实现最高 **20x 压缩**且性能损失极小。对 Hermes 的直接价值：每次系统 prompt + memory + skills 注入约 2000+ tokens，压缩后可能降至 200-500，每次对话节省 75% 输入成本。

## 🛠️ 底层原理解析

- **核心逻辑描述：** 用小模型对 prompt 做逐 token 困惑度评分 → 低信息量 token（停用词、冗余修饰）标记为可移除 → 按目标压缩比保留高信息量 token。LLMLingua-2 用 BERT 做 token 分类，3-6x 更快。

- **关键机制：**

```python
# 核心 API — 三行压缩
from llmlingua import PromptCompressor
compressor = PromptCompressor(model_name="microsoft/llmlingua-2-bert-base")
compressed = compressor.compress_prompt(
    original_prompt, 
    rate=0.5,          # 保留 50% token
    force_tokens=["\n", "?", ".", "API_KEY"]  # 强制保留
)

# 三种变体：
# LLMLingua: 基于困惑度的 token 级压缩（小模型打分）
# LongLLMLingua: 长文本专用，解决"迷失中间"问题
# LLMLingua-2: BERT 级蒸馏，3-6x 更快，任务无关

# 核心算法（简化）：
# 1. 小 LM 前向传播 → 每个 token 的 log probability
# 2. 按 perplexity 排序 → 低信息量 token 排前面
# 3. 迭代移除直到达到目标压缩比
# 4. 保持原始语义结构（段落边界、标点）
```

## 🔄 Hermes 进化映射 (Integration Roadmap)

- **关联现有技能：** [[ai-commander-system]], [[model-router]], [[claude-obsidian-architecture]]

| 应用场景 | 改造方案 | 预期节省 |
|---|---|---|
| 系统 prompt 压缩 | 用 LLMLingua-2 压缩 Hermes 的 AGENTS.md + memory 注入 | ~70% 输入 |
| 长文档摘要 | 飞轮扫描到的长 README 先压缩再分析 | ~80% 上下文 |
| Skill 懒加载 | 只加载 skill 摘要，详细内容按需解压 | ~60% 冷启动 |
| 历史对话压缩 | 压缩过去的会话上下文而非截断 | ~50% 上下文保持 |
