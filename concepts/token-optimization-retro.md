---
id: 20260531-token-optimization-retro
title: 飞轮 Token 优化复盘 — 从 53万/篇 → 5万/篇的改造
tags: [token-optimization, flywheel, skill-upgrade, 自研]
date_created: 2026-05-31
confidence: high
---

## 🎯 WHAT — 问题

3轮飞轮产出了 9 篇 Wiki，消耗 ~480万 tokens，平均 53万/篇。

**浪费分布：**
```
子Agent 源码抓取    60%  (读 1964行 state.py, 6850行 parser.py...)
我的验证修复        15%  (竞态 index.md → 反复读修)
失败重试           10%  (3/9 子Agent 超时/404)
子Agent prompt开销  10%  (系统提示 + 任务描述)
其他                5%
─────────────────────────
                  100%  = ~4.8M tokens
```

## 🛠️ HOW — 改造项

### 1. 预筛选（Hermes 自己做）
```
之前: 扫描 3 方向 → 全量拆解 3 篇
现在: 扫描 3-5 方向 → Hermes 评分 → 只拆 Top 1-2 篇
节省: 每轮少拆 1-2 篇 → -50%
```

### 2. 子Agent 限流（硬限制）
```
之前: 子Agent 随意抓源码，经常读 10+ 文件
现在: README ≤ 400行 + 源文件 ≤ 2个(各300行) + Wiki ≤ 300行
节省: 单篇 50K→15K → -70%
```

### 3. 索引集中更新（消除竞态）
```
之前: 子Agent 各自更新 index.md → 竞态 → Hermes 反复修复
现在: 子Agent 只写 Wiki 正文 → Hermes 最后一次性更新所有索引
节省: 验证/修复 token → -100%
```

### 4. 失败不重试
```
之前: 子Agent 超时 → 重新委托 → 又超时 → 手动补
现在: 超时 → 150行简版替代，不二次委托
节省: 失败重试 token → -100%
```

## 🔄 APPLICATION — 预期效果

```
                    之前        之后
每轮 Wiki 数        3 篇       1-2 篇
每篇 token          53万       3-5万
每轮 token          ~160万     ~8万
效率提升            1x         ~20x
```

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初始 | 2026-05-31 | 复盘 4.8M token 消耗，落地 4 项改造，更新 knowledge-flywheel + project-commander skill |
