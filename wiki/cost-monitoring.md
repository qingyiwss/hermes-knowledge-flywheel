# 成本监控与预警
> 创建: 2026-06-20 · 迭代: 第2轮 · 作者: Hermes (mimo-v2.5-pro)

## 监控指标

| 指标 | 公式 | 预警阈值 |
|------|------|:---:|
| 日均费用 | 总费用 / 天数 | >¥20/天 |
| 缓存命中率 | 缓存命中 / 总输入 | <50% |
| 每轮平均 Token | 总 Token / 总轮次 | >5000/轮 |
| 子代理失败率 | 失败任务 / 总任务 | >30% |
| CC 重做率 | 重做次数 / 总提交 | >20% |

## 当前基准（MiMo 时代）

| 项目 | 值 |
|------|------|
| 每轮平均消耗 | 3000-5000 Token |
| 缓存命中率目标 | >70% |
| 日均费用预估 | ¥5-10（中等使用） |
| 峰值费用预估 | ¥15-20（重负载） |

## 成本构成分析

典型会话成本分解：

```
输入 Token（含缓存）  40-50%
输出 Token           30-40%
思考 Token（推理）    10-20%
工具调用 Token        5-10%
```

## 优化杠杆

### 1. 缓存命中率（最大杠杆）
- **目标**：>70%
- **方法**：保持系统提示稳定、工具定义固定、使用 session-sticky routing
- **收益**：70% 命中率时平均输入价格降 69%

### 2. 辅助模型分层
- **网页摘要**：mimo-v2-flash（省 75%）
- **代码搜索**：mimo-v2-flash（省 75%）
- **复杂推理**：mimo-v2.5-pro（保留）
- **子代理**：mimo-v2-flash（省 75%）

### 3. 输出长度控制
- MiMo 本身已很简洁（#4/92）
- 对于报告类任务，指定"简洁输出"或"不超过 X 字"
- 代码生成：要求只输出变更部分，不输出完整文件

### 4. 任务描述精度
- **CC 场景**：精确描述 → 一步到位 → 省 2-3 轮重做
- **规则**：任务描述多花 30 秒写精确，省 2-3 分钟重做

### 5. no_agent 模式
- **适用**：监控、数据采集、定时报告
- **收益**：零 Token 消耗
- **案例**：hosting-price-tracker、waitlist-counter

## 每日成本报告脚本

```bash
#!/bin/bash
# 从 W&B 或 API 日志提取每日费用
# 建议用 cron 每天 23:00 运行

DATE=$(date +%Y-%m-%d)
LOG_FILE="/root/.hermes/logs/api_calls_${DATE}.json"

if [ -f "$LOG_FILE" ]; then
  TOTAL=$(jq '[.[].cost] | add' "$LOG_FILE")
  CACHE_HITS=$(jq '[.[].cache_hit // false] | map(select(. == true)) | length' "$LOG_FILE")
  TOTAL_CALLS=$(jq 'length' "$LOG_FILE")
  HIT_RATE=$(echo "scale=1; $CACHE_HITS * 100 / $TOTAL_CALLS" | bc)
  
  echo "📊 每日成本报告: $DATE"
  echo "总费用: ¥$TOTAL"
  echo "缓存命中率: ${HIT_RATE}%"
  echo "总调用: $TOTAL_CALLS 次"
  
  # 预警
  if (( $(echo "$TOTAL > 20" | bc -l) )); then
    echo "⚠️ 费用超限: ¥$TOTAL > ¥20/天"
  fi
  if (( $(echo "$HIT_RATE < 50" | bc -l) )); then
    echo "⚠️ 缓存命中率过低: ${HIT_RATE}% < 50%"
  fi
fi
```

## W&B 集成

如果已配置 Weights & Biases：
- `finish_reason: cached` 标记缓存命中
- 可按模型/任务/时间段筛选费用
- 设置预算告警（>¥20/天触发通知）

## 参考

- Portkey: 7 策略控制 LLM 成本 (2026-06)
- Ingest Labs: LLM API 成本控制 (2026-04)
- 墨天轮: 管好 Token 成本 (2026-05)
