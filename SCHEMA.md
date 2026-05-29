# Wiki Schema

## Domain
用户的知识体系：投资策略分析、AI自媒体运营、公司/项目管理。
三个领域互有交叉——投资策略通过自媒体输出，公司作为法律主体承载运营。

## Conventions
- 文件名：小写连字符，如 `valuation-dca-strategy.md`
- 每个 wiki 页面带 YAML frontmatter
- 使用 `[[wikilinks]]` 互相链接，每页至少 2 个出链
- 更新页面必须更新 `updated` 日期
- 新页面必须添加到 `index.md` 对应分类
- 每次操作记录到 `log.md`
- 含 3+ 来源的页面，段落末尾加 `^[raw/xxx]` 来源标记

## Frontmatter
```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [见下方分类]
sources: [raw/articles/source-name.md]
confidence: high | medium | low
---
```

## Tag Taxonomy

### 投资策略
- `strategy` — 策略方案
- `valuation` — 估值分析
- `backtest` — 回测相关
- `portfolio` — 组合管理
- `market` — 市场行情
- `risk` — 风险管理

### AI/自媒体
- `ai-model` — AI 模型相关
- `content` — 内容创作
- `automation` — 自动化工具
- `platform` — 平台运营
- `monetization` — 变现

### 公司运营
- `legal` — 工商法务
- `finance` — 财税
- `ops` — 运营管理
- `product` — 产品开发
- `team` — 团队

### 工具/系统
- `reasonix` — Reasonix 相关
- `hermes` — Hermes Agent 相关
- `claude-code` — Claude Code 相关

### 元
- `meta` — 知识库自身的元信息
- `comparison` — 对比分析
- `timeline` — 时间线

规则：页面 tag 必须在上述分类中。新增 tag 先更新此文件。

## Page Thresholds
- 一个实体/概念出现在 2+ 来源 或 作为单一来源核心 → 建页
- 仅次要提及 → 不建页
- 页面超过 200 行 → 拆分
- 完全被替代的页面 → 移至 `_archive/`

## 三大领域页面结构

### 投资策略页
- 策略逻辑
- 参数（PE百分位阈值、定投金额档位）
- 回测结果摘要
- [[相关策略对比]]
- 来源和置信度

### AI/自媒体页
- 工具/模型简介
- 使用方案
- 效果数据
- [[竞品对比]]

### 公司运营页
- 基本信息（名称、注册资本、经营范围）
- 办理流程和进度
- 关键节点（核名→执照→开户→税务）
- 成本记录
