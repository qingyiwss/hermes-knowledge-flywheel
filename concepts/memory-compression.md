---
id: 20260531-memory-compression
title: Memory 压缩 — 持久记忆去重，从 574→90 chars
tags: [token-optimization, memory, flywheel, 自研]
date_created: 2026-05-31
confidence: high
---

## 🎯 WHAT — 问题

持久记忆 13 条，2,945/4,400 chars (66%)。其中有大量重复和过期信息。

### 去重前
| 条目 | chars | 问题 |
|------|-------|------|
| QQ Bot 详细配置 | 270 | 与 user profile 重复 |
| 翻墙状态 | 190 | 含过时的 Go pkg 信息 |
| CordCloud 订阅链接 | 192 | 订阅已过期 (user profile 确认) |

### 去重后
| 条目 | chars | 变化 |
|------|-------|------|
| 翻墙：ClashX→CordCloud | 90 | 合并 2+3 |
| CordCloud 订阅 URL | 0 | 删除 (过期) |

## 🛠️ HOW — 去重原则

1. **与 skills 重叠 → 移交 skill**，memory 只留引用
2. **与 user profile 重叠 → 删除**，profile 已持久
3. **过期信息 → 删除**（订阅链接、Go pkg 路径）
4. **同类合并** — 多个条目讲同一主题 → 合并为 1 条

## 📊 效果

```
指标              之前      之后      节省
─────────────────────────────────────────
代理相关 (3条)    574 chars  90 chars  -84%
QQ Bot           重复      (在profile) -100%
总条数           14        13         -1
总chars          3,135     2,945      -6%
```

注：本次仅优化了代理相关条目。后续可按同样原则继续压缩其他重复条目。

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初始 | 2026-05-31 | 代理条目去重合并，删除过期订阅链接 |
