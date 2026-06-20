# Token 消耗优化 — NΞXUS 实战指南
> 创建: 2026-06-20 · 迭代: 第1轮 · 作者: Hermes (mimo-v2.5-pro)

## 核心数据

| 模型 | 输入(缓存未命中) | 输入(缓存命中) | 输出 | 节省率 |
|------|:---:|:---:|:---:|------|
| MiMo-V2.5-Pro | ¥3/百万 | ¥0.025/百万 | ¥6/百万 | 缓存命中 **99.2%** |
| MiMo-V2-Flash | ¥0.70/百万 | ¥0.07/百万 | ¥2.10/百万 | 缓存命中 **90%** |
| DeepSeek V4 Pro | $1.74/百万 | — | $3.48/百万 | 无缓存 |

> MiMo 的缓存价格优势极其显著：缓存命中后输入成本降至原来的 0.8%。

## 七大优化策略

### 策略1: LCM 激进压缩
上下文压缩是最大的 Token 节省手段。

```env
LCM_CONTEXT_THRESHOLD=0.20      # 200K token 就触发（原 0.45）
LCM_FRESH_TAIL_COUNT=12         # 只保留最近 12 条不压缩
LCM_CACHE_FRIENDLY_CONDENSATION_ENABLED=true
```

**效果**：长会话（85K+ token）压缩后降至 15-20K，节省 75-80%。

### 策略2: 工具搜索阈值
```bash
hermes config set tools.tool_search.threshold_pct 3
```
默认 10% 多注入 ~2,300 tokens/轮。改为 3% 后节省 70% 的工具描述注入。

### 策略3: 子代理超时缩短
```bash
hermes config set delegation.child_timeout_seconds 300
hermes config set delegation.max_iterations 15
```
默认 600s 超时 + 20 轮迭代。缩短后避免子代理空转浪费 Token。

### 策略4: 辅助模型分层
不是所有任务都需要主模型。辅助任务用 Flash 级模型：

| 任务类型 | 模型 | 费用 |
|---------|------|------|
| 主对话 | mimo-v2.5-pro | ¥3/百万 |
| 网页摘要 | mimo-v2-flash | ¥0.70/百万 |
| 子代理 | mimo-v2-flash | ¥0.70/百万 |
| 兜底 | mimo-v2-flash | ¥0.70/百万 |

**效果**：辅助任务费用降至 1/4。

### 策略5: no_agent Cron 模式
定时报告类任务不经过 LLM，零 Token：

```python
# cron job 设置 no_agent=true
# 脚本直接输出 → cron 投递 → 不经 LLM
```

适用：量化日报、系统监控、价格追踪、参数巡检。

### 策略6: 精简 Skill 注入
Skill 加载是隐性 Token 消耗大户。一个大 Skill（如 nexus-core）可能占 5,000+ tokens。

**优化**：
- `tools.tool_search.threshold_pct: 3` 减少工具描述注入
- 只加载相关 Skill，不全量注入
- Skill 内容保持精简，详细内容放 references/ 按需加载

### 策略7: 输出控制
```bash
hermes config set agent.max_turns 150
```
限制最大轮数，避免长对话链浪费。配合 LCM 压缩使用。

## Token 消耗基线（NΞXUS 典型会话）

| 操作 | 预估 Token | 费用(MiMo) |
|------|:---:|:---:|
| 简单查询（不加载 Skill） | 5-10K | ¥0.015-0.03 |
| 中等任务（1-2 Skill + CC） | 20-40K | ¥0.06-0.12 |
| 复杂构建（5+ CC 任务） | 80-150K | ¥0.24-0.45 |
| 飞轮沉淀（调研+写 Wiki） | 50-80K | ¥0.15-0.24 |

## 测量方法

每次任务结束时检查消耗：
```
Hermes · mimo-v2.5-pro · 本次消耗 ~XK tokens
```

如果单次操作 >50K tokens，检查是否有优化空间。

## 参考

- Airbnb 6 周项目省 60-80%: Medium Predict (2026-05)
- Token-Per-Task Economics: LinkedIn (2025-12)
- LLM Token Optimization: Reintech (2025-12)
