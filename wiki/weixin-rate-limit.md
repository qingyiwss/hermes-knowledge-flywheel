---
id: 20260531-weixin-rate-limit
title: 微信断流诊断与根治 — iLink 频率限制的防御体系
tags: [weixin, gateway, bug-fix, reliability, 自研]
date_created: 2026-05-31
confidence: high
---

## 🎯 WHAT — 现象

5 轮 Token 飞轮任务中，飞轮 3/4/5 的回复未送达微信端。用户只看到飞轮 2 之后的内容消失。

```
时间线:
16:46  飞轮2 完成，回复送达 ✅
16:46  开始密集工具调用 (59 API calls, 544.9s)
16:59  首次 rate limited 出现 ← 断流开始
17:00  "send failed" × 34 次
17:04  用户发"任务进行到哪了" ← 没收到飞轮3-5
```

## 🔍 根因：iLink 频率限制 (ret=-2)

```python
# weixin.py L95
RATE_LIMIT_ERRCODE = -2  # iLink frequency limit

# L1690-1705: 频率限制 → 3s backoff → retry
if is_rate_limited:
    wait = self._send_chunk_retry_delay_seconds * 3  # 3s
    await asyncio.sleep(wait)
    continue  # 最多 4 次重试
```

### 恶化链

```
长任务 (544s, 59 API calls)
  → 中间产出大量 progress message
    → 每条消息拆分为多个 chunk (1.5s 间隔)
      → iLink 累积限流 (未公开 QPS 限制)
        → retry 触发更多请求
          → 雪崩：178 次 rate limit + 34 次 send failed
            → 消息丢失 ❌
```

### 关键配置

| 参数 | 默认值 | 作用 |
|------|--------|------|
| `send_chunk_delay_seconds` | 1.5s | chunk 间延迟 |
| `send_chunk_retries` | 4 | 每条 chunk 重试次数 |
| `send_chunk_retry_delay_seconds` | 1.0s | rate limit 时的 backoff 基数 |

## 🛠️ 解决方案 (4 层防御)

### 层 1：增加 chunk 延迟 (立即生效)
```bash
export WEIXIN_SEND_CHUNK_DELAY_SECONDS=3.0  # 1.5 → 3.0
```
每条 chunk 间等 3s，减少 iLink 压力。

### 层 2：减少 chunk 数量 — 压缩中间输出
当前每次 tool call 可能产生独立的"进度消息"。修改策略：
- 工具执行中：不给 WeChat 发进度更新
- 只在最终回复时一次性发送

### 层 3：长消息自动总结
超过一定长度的回复自动压缩为摘要 + "详情已保存到本地文件"。

### 层 4：重试退避指数化
当前 3×1.0=3s 固定退避 → 改为指数退避 1s, 3s, 9s, 27s。

## 🔧 落地步骤

### Step 1: 增加 chunk 延迟 + 减少重试 (避免重试风暴)
```bash
export WEIXIN_SEND_CHUNK_DELAY_SECONDS=3.0
export WEIXIN_SEND_CHUNK_RETRIES=2  # 4→2，减少重试风暴
```

### Step 2: 网关配置持久化
写入 gateway 启动配置，确保重启后生效。

### Step 3: 本地文件容灾
关键回复同时写入 `~/.hermes/weixin-fallback/` 目录备查。

## 📊 预期效果

| 指标 | 之前 | 之后 | 
|------|------|------|
| chunk 间隔 | 1.5s | 3.0s |
| 重试次数 | 4 | 2 (降低风暴) |
| rate limit 事件 | 178/任务 | ~0 |
| 消息丢失 | 34/任务 | ~0 |

根本原则：**iLink 不可对抗，只能顺从。** 放慢发送节奏，减少无效重试。

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 发现 | 2026-05-31 | gateway.log 诊断：178 次 rate limit + 34 次 send failed |
| 修复 | 2026-05-31 | chunk_delay 1.5→3.0s, retries 4→2 |
