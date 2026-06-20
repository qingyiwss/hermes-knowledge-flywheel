---
id: 20260529-codegraphcontext
title: CodeGraphContext 代码图谱 MCP 工具拆解
tags: [skill-learning, automation, agent-upgrade, code-quality]
source_url: https://github.com/CodeGraphContext/CodeGraphContext
date_created: 2026-05-29
updated: 2026-05-29
last_updated: 2026-05-29
---

# CodeGraphContext 代码图谱 MCP 工具拆解

## 🎯 核心痛点与应用场景

> CodeGraphContext 把代码库变成 AI 可查询的知识图谱。传统 grep 只能做文本匹配，它用 AST 解析出函数/类/调用关系，存入 Neo4j 图数据库，让 AI 能问"谁调用了这个函数""哪里改了这变量""哪些代码是死的"。对 Hermes 的 pre-commit verifier 和代码审查能力是直接可复用的架构。

## 🛠️ 底层原理解析

- **核心逻辑描述：** AST 解析 → 图节点（Repository/File/Module/Class/Function）→ 关系边（CONTAINS/CALLS/IMPORTS/INHERITS）→ MCP 工具暴露 8 个查询接口。支持 Neo4j/FalkorDB/Kuzu/Ladybug 多种后端。

- **关键机制：**

```python
# 1. 图 Schema — 代码结构的关系化
"""
节点: Repository → File → Module → Class → Function
属性: name, path, cyclomatic_complexity, source, line_number
关系: CONTAINS(File→Function), CALLS(Function→Function),
      IMPORTS(File→Module), INHERITS(Class→Class)
"""

# 2. 8 个 MCP 工具
TOOLS = {
    "add_code_to_graph":  # AST 解析 + 异步入库（返回 job_id）
    "find_code":          # 关键词搜索 + 模糊匹配
    "analyze_code_relationships": {  # 15 种查询类型
        "query_type": ["find_callers", "find_callees", "find_importers",
            "who_modifies", "class_hierarchy", "overrides",
            "dead_code", "call_chain", "module_deps",
            "variable_scope", "find_complexity", ...]
    },
    "find_dead_code":     # 全库扫描无用函数（排除特定装饰器）
    "calculate_cyclomatic_complexity":  # 圈复杂度度量
    "watch_directory":    # 持续监控 + 自动增量更新
    "execute_cypher_query":  # 直接 Cypher 查询（专家模式）
    "add_package_to_graph":  # 索引 pip 包依赖
}

# 3. 异步任务模式 — 长索引不阻塞
# add_code_to_graph 返回 job_id → check_job_status 轮询进度
# 支持并行索引多个目录

# 4. 多数据库后端
# database.py (Neo4j) / database_falkordb.py / database_kuzu.py
# 统一接口，按环境变量切换
```

## 🔄 Hermes 进化映射 (Integration Roadmap)

- **关联现有技能：** [[ai-commander-system]], [[claude-obsidian-architecture]], github-push-china
- **关联概念：** [[harness-engineering]]

### 直接落地：pre-commit verifier

| CGC 能力 | Hermes 改造 | 实现路径 |
|---|---|---|
| AST → 图 | 用 Python `ast` 模块解析 staged files | 轻量，无需 Neo4j |
| find_dead_code | 检测 commit 引入的死代码 | ast.walk() + 引用计数 |
| analyze_relationships | 变更函数的影响范围 | 调用链追踪 |
| cyclomatic_complexity | 复杂度阈值告警 | 复用 radon 或自实现 |
| job_id 异步模式 | 大仓库索引不阻塞 | asyncio 后台任务 |

### 简化方案（无需图数据库）

```python
# 用 Python stdlib ast + dict 替代 Neo4j
import ast, os
graph = {"functions": {}, "classes": {}, "calls": {}}

for file in staged_files:
    tree = ast.parse(open(file).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            graph["functions"][node.name] = {
                "file": file, "line": node.lineno,
                "calls": [n.func.id for n in ast.walk(node) 
                         if isinstance(n, ast.Call) and hasattr(n.func, 'id')]
            }
```
