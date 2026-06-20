# 实战验证 — Token/缓存/效率优化
> 创建: 2026-06-20 · 迭代: 第5轮 · 作者: Hermes (mimo-v2.5-pro)

## 验证框架

### 1. 缓存命中率验证
**方法**：
```bash
# 从 API 日志提取缓存命中率
grep -r "cache_hit" /root/.hermes/logs/ | \
  awk '{if($NF=="true") hit++; total++} END {print "命中率:", hit/total*100 "%"}'
```
**目标**：>70%
**频率**：每日

### 2. Token 消耗验证
**方法**：
```bash
# 从 API 日志提取每轮平均 Token
jq '.usage.total_tokens' /root/.hermes/logs/api_calls_*.json | \
  awk '{sum+=$1; count++} END {print "平均每轮:", sum/count}'
```
**目标**：<3000 Token/轮
**频率**：每日

### 3. 成本验证
**方法**：
```bash
# 从 API 日志提取每日费用
jq '.cost' /root/.hermes/logs/api_calls_*.json | \
  awk '{sum+=$1} END {print "日均费用: ¥" sum}'
```
**目标**：<¥10/天
**频率**：每日

### 4. CC 重做率验证
**方法**：
```bash
# 从 CC 日志提取重做次数
grep -c "重做\|redo\|retry" /root/.hermes/logs/cc_*.log
```
**目标**：<20%
**频率**：每周

### 5. 子代理失败率验证
**方法**：
```bash
# 从子代理日志提取失败率
grep -c "失败\|error\|timeout" /root/.hermes/logs/delegate_*.log
```
**目标**：<20%
**频率**：每周

## 验证时间表

| 验证项 | 频率 | 负责人 | 工具 |
|------|:---:|:---:|------|
| 缓存命中率 | 每日 | Hermes | cron no_agent |
| Token 消耗 | 每日 | Hermes | cron no_agent |
| 成本报告 | 每日 | Hermes | cron no_agent |
| CC 重做率 | 每周 | Hermes | 手动检查 |
| 子代理失败率 | 每周 | Hermes | 手动检查 |

## 调整策略

### 缓存命中率 <50%
**可能原因**：
- 系统提示频繁变更
- 工具定义不稳定
- 会话频繁切换

**调整**：
1. 检查系统提示是否稳定
2. 检查工具定义是否固定
3. 启用 Session-sticky routing

### Token 消耗 >5000/轮
**可能原因**：
- 输出过长
- 工具调用过多
- 任务描述不精确

**调整**：
1. 启用压缩输出
2. 优化工具选择
3. 提高任务描述精度

### 成本 >¥20/天
**可能原因**：
- 缓存命中率低
- 输出 Token 过多
- 子代理调用过多

**调整**：
1. 提高缓存命中率
2. 压缩输出
3. 优化子代理调用

## 实战案例

### 案例 1：网页研究任务
**任务**：搜索并总结 5 个网页
**优化前**：
- 5 次 browser_navigate（50,000 Token）
- 5 次 browser_snapshot（25,000 Token）
- 总计：75,000 Token

**优化后**：
- 1 次 web_search（500 Token）
- 1 次 web_extract（2,000 Token）
- 总计：2,500 Token

**节省**：97%

### 案例 2：代码任务
**任务**：修复一个 bug
**优化前**：
- "修复登录 bug"（模糊描述）
- CC 猜测 → 3 轮重做
- 总计：15,000 Token

**优化后**：
- "修复 LoginModal.tsx 第 23 行空指针：email 为空时未检查"（精确描述）
- CC 一步到位
- 总计：5,000 Token

**节省**：67%

### 案例 3：监控任务
**任务**：每 5 分钟检查 API 健康
**优化前**：
- cron agent 模式
- 每次 500 Token
- 日总计：144,000 Token

**优化后**：
- cron no_agent 模式
- 每次 0 Token（异常时才有输出）
- 日总计：0 Token

**节省**：100%

## 参考

- NΞXUS 内部实战经验
- Anthropic: Claude 最佳实践 (2026-06)
- ProjectDiscovery: 缓存命中率优化 (2026-06)
