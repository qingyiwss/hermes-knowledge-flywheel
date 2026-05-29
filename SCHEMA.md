# 知识飞轮运行规则

## 扫描周期
每 3-7 天执行一轮扫描，精选 1-2 个高价值开源项目深度拆解。

## 筛选标准
- 代码量适中（核心逻辑 ≤ 500 行）
- 可直接通过 Python/Shell/Prompt 落地
- 解决 Hermes 当前能力短板
- 优先 CLI 工具、Agent 框架、自动化脚本

## 拆解三问（WHAT/HOW/APPLICATION）
每篇笔记必须回答：
1. **WHAT**: 解决了什么痛点？底层原理？
2. **HOW**: 核心实现逻辑（附关键代码 + 注释）
3. **APPLICATION**: 如何在 Hermes 系统中集成？

## 笔记模板

```markdown
---
id: YYYYMMDD-HHMMSS
title: 知识点名称
tags: [skill-learning, 技术标签]
source_url: GitHub 仓库链接
date_created: YYYY-MM-DD
---

# 知识点名称

## 🎯 WHAT — 核心问题与原理
- 解决了什么？
- 底层原理是什么？

## 🛠️ HOW — 关键实现
- 核心代码段：
```python
# 带注释的关键代码
```

## 🔄 APPLICATION — Hermes 集成方案
- 关联现有技能：[[技能A]], [[技能B]]
- 改造路径：修改 `具体模块/Prompt段落`
- 预期效果：...

## 📊 进化日志
- 本轮学到了什么？
- 下一步计划？
```

## Git 提交规范
```
feat(notes): 拆解 [项目名] — [一句话总结]
```

每次提交必须附带一条 growth-log.md 追加条目。
