# 执行效率优化 — NΞXUS 实战指南
> 创建: 2026-06-20 · 迭代: 第1轮 · 作者: Hermes (mimo-v2.5-pro)

## 效率公式

```
执行效率 = 有价值产出 / (Token消耗 × 时间)
```

三个杠杆：减少 Token、缩短时间、提高产出质量。

## 策略1: 并行任务拆分

### delegate_task 批量模式

单任务串行：总时间 = T1 + T2 + T3
三任务并行：总时间 = max(T1, T2, T3)

**限制**：`delegation.max_concurrent_children` 默认 3

### 拆分原则

| 原则 | 示例 |
|------|------|
| 每任务 1-2 文件 | 文件过多 → 拆 |
| 每任务 60-120 秒 | 超过 120s → 拆 |
| 任务间可独立 | 有依赖 → 串行 |
| 验证点前置 | 每任务后立即验证 |

**实战案例**：
- Transcribo SaaS：5 个子任务，每个 60-135 秒，总耗时 ~150 秒（串行需 400+ 秒）
- TradeCRM v1.0：6 个子任务，每个 100-180 秒，总耗时 ~200 秒

## 策略2: Loop Engineering

用条件循环代替人工反复指令。

### hermes-cc-loop.sh（条件触发）

```bash
hermes-cc-loop.sh -c "npx tsc --noEmit" -m 5 -d /root/code/project "修复类型错误"
```

**流程**：CC 执行 → 验证命令 → 不过？循环 → 通过或超限停止

**效率提升**：原本需要人工 3-5 轮对话才能修好的 bug，自动循环 1-3 轮搞定。

### hermes-cc-worktree.sh（工作区隔离）

```bash
hermes-cc-worktree.sh -r /root/code/quant -b fix-macd "修复 MACD 计算"
```

**流程**：创建 worktree → CC 在隔离区修复 → 提交 → 推送

**效率提升**：多个 bug 可以并行在不同 worktree 修复，互不干扰。

## 策略3: no_agent Cron 模式

定时任务不经过 LLM，零 Token + 零延迟：

| 模式 | Token | 延迟 | 适用 |
|------|:---:|:---:|------|
| 智能体模式（默认） | 高 | 30-60s | 需要推理的任务 |
| no_agent 模式 | **0** | **<5s** | 数据采集/监控/报告 |

**NΞXUS 已用 no_agent 的任务**：
- 量化日报（quant-daily-report.py）
- CRM 跟进提醒（trade-followup-reminder.py）
- 外贸回信监控（trade-reply-monitor.py）
- 优化参数巡检（check-opt-params.py）

## 策略4: 子代理任务描述优化

任务描述越精确，CC 执行越快：

**反面**：
```
"把这个页面优化一下，让它看起来更好"
```
→ CC 猜测 → 可能方向错 → 重做 → 浪费 2-3 轮

**正面**：
```
"在 products.html 的 #makeup-brushes 段落，添加一个 bristle 
材质对比表（6行，列为：材质/类型/单价/最佳用途/核心优势），
使用 specs-table CSS 类，放在现有 specs-table 前面"
```
→ CC 一步到位 → 一次成功

## 策略5: Skill 预加载

Cron 任务可以通过 `skills` 参数预加载相关 Skill，避免 CC 自己搜索知识：

```json
{
  "skills": ["foreign-trade-customer-dev", "foreign-trade-sourcing"],
  "prompt": "..."
}
```

**效果**：CC 直接有完整上下文，减少额外搜索和推理。

## 策略6: 验证前置

每步验证，不等全部完成再查：

```
CC 写 Auth 页面 → tsc 验证 → 过 ✓
CC 写 Products 页面 → tsc 验证 → 错 → 退回 CC 修 → 再验 → 过 ✓
CC 写 API Routes → tsc 验证 → 过 ✓
全部完成 → 最终构建 → 成功
```

**vs**

```
CC 写所有文件 → 最终构建 → 10 个错误 → 排查 30 分钟
```

## 效率指标（NΞXUS 基线）

| 指标 | 基线 | 目标 |
|------|------|------|
| CC 单任务耗时 | 60-120s | <120s |
| CC 超时率 | <5% | <2% |
| Hermes 验证通过率 | >80% | >90% |
| 缓存命中率 | >60% | >80% |
| 长会话 Token | <100K | <60K（LCM 压缩） |

## 参考

- Loop Engineering 概念: YouTube AI 编程视频 (2026)
- ProjectDiscovery: 40 步任务的缓存优化 (2026-04)
- Reddit/ClaudeAI: Git Worktree 并行 Agent (2025-05)
- Addy Osmani: Future of Agentic Coding (2026-01)
