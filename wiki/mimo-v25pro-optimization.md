# MiMo-V2.5-Pro 模型特有优化
> 创建: 2026-06-20 · 迭代: 第2轮 · 作者: Hermes (mimo-v2.5-pro)

## 模型画像

| 属性 | 值 |
|------|------|
| 总参数 | 1.02T（MoE 架构） |
| 活跃参数 | 42B / token |
| 上下文窗口 | 1M token |
| 最大输出 | 128K token |
| 智能指数 | #5/92（Artificial Analysis） |
| 输出速度 | 54 token/s（#43/92，偏慢） |
| 简洁度 | #4/92（非常简洁） |
| 许可证 | MIT（开源） |
| 推理模式 | 是（链式思考） |

## 缓存价格（杀手级优势）

| 类型 | 价格 | 对比 |
|------|------|------|
| 缓存未命中 | $0.435/百万 | 基准 |
| 缓存命中 | **$0.004/百万** | **省 99%** |
| 输出 | $0.87/百万 | — |

> **MiMo 缓存命中价格 $0.004/百万是当前市场最低**，比 DeepSeek V4 Pro 全价 $1.74 低 435 倍。

## 推理模型的 Token 消耗特征

MiMo 是推理模型，内部会做链式思考（Chain-of-Thought），这会消耗额外 Token：

| 任务类型 | 表面输出 | 实际思考 Token | 总消耗 |
|---------|:---:|:---:|:---:|
| 简单查询 | 200 | 500-1000 | 700-1200 |
| 中等任务 | 500 | 2000-5000 | 2500-5500 |
| 复杂推理 | 1000 | 5000-15000 | 6000-16000 |

**优化**：
- 简单任务不需要深度推理 → 用 `mimo-v2-flash`（非推理模型，更快更省）
- 只有复杂任务才用 `mimo-v2.5-pro`
- NΞXUS 当前配置已做到：主模型 Pro，子代理/辅助 Flash

## 简洁度优势

MiMo 在 #4/92 最简洁模型中排名，平均输出比同类模型少 13%。

**对 NΞXUS 的意义**：
- 输出更精炼，减少输出 Token 消耗
- 但需要注意：过度简洁可能遗漏细节
- 对于需要详细报告的场景，可以在 prompt 中要求详细输出

## 速度特征

54 token/s，比平均值 62 慢 13%。

**影响**：
- 对话响应略慢（用户感知约 +0.5-1 秒）
- 但缓存命中后延迟大幅降低（TTFT 快 85%）
- 对 CC 代码生成：整体影响不大（代码生成主要瓶颈是 Token 数量而非速度）

## 与 DeepSeek V4 Pro 的对比

| 维度 | MiMo-V2.5-Pro | DeepSeek V4 Pro | MiMo 优势 |
|------|:---:|:---:|------|
| 智能体任务 | 68.4 | 59.1 | **+15.7%** |
| 编程能力 | 57.2 | 58.8 | -2.8% |
| 缓存价格 | $0.004/M | 无缓存 | **435 倍差距** |
| 输出简洁度 | #4/92 | 中等 | 更省 Token |
| 速度 | 54 t/s | ~60 t/s | -10% |
| 推理模式 | 链式思考 | 非推理 | 更强但更贵 |

## Hermes 配置优化建议

```yaml
# config.yaml 最优配置
model:
  default: mimo-v2.5-pro
  provider: xiaomi
  base_url: https://token-plan-cn.xiaomimimo.com/v1

providers:
  xiaomi:
    base_url: https://token-plan-cn.xiaomimimo.com/v1
    api_key_env: MIMO_API_KEY

# 辅助模型分层
auxiliary:
  web_extract:
    model: mimo-v2-flash      # 网页摘要用 Flash
    timeout: 600

# 子代理配置
delegation:
  child_timeout_seconds: 300
  max_iterations: 15

# 工具搜索优化
tools:
  tool_search:
    threshold_pct: 3
```

## Claude Code (CC) 配置

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://token-plan-cn.xiaomimimo.com/anthropic",
    "ANTHROPIC_MODEL": "mimo-v2.5-pro",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "mimo-v2.5-pro",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "mimo-v2.5-pro",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "mimo-v2-flash",
    "CLAUDE_CODE_SUBAGENT_MODEL": "mimo-v2-flash",
    "CLAUDE_CODE_EFFORT_LEVEL": "max"
  }
}
```

## 参考

- Artificial Analysis: MiMo-V2.5-Pro 智能/速度/价格分析 (2026-04)
- Xiaomi MiMo 官方文档: platform.xiaomimimo.com
- BenchLM: DeepSeek V4 Pro vs MiMo-V2.5-Pro (2026-06)
