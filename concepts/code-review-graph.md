---
id: 20260531-code-review-graph
title: code-review-graph 拆解 — Tree-sitter AST 图谱、GraphRAG、MCP 30 工具、秒级增量更新
tags: [code-quality, mcp, graphrag, agent-upgrade, skill-learning, automation]
source_url: https://github.com/tirth8205/code-review-graph
date_created: 2026-05-31
last_updated: 2026-05-31
confidence: high
---

# code-review-graph 拆解

> ⭐ 17,731 | MIT License | Python 3.10+ | PyPI: `code-review-graph` | 官网: code-review-graph.com

## 🎯 WHAT — 核心问题与原理

### 它解决什么？

AI 编码工具在代码审查时会把整个仓库读进上下文——**一个 500 文件的项目 ≈ 10 万+ token，93% 与当前变更无关**。code-review-graph 用 Tree-sitter 把代码库解析成结构化的**知识图谱**，变更时只抽取"爆炸半径"内的文件，实现 **38x–528x token 压缩**。

### 核心理念：先建图，再审查

> 传统 grep/全文搜索 = 文本匹配。code-review-graph = 代码结构理解 + 依赖关系追踪。

不是让 AI "看"代码，而是让 AI **查询一张已经建好的图**：谁调用了这个函数？哪些测试覆盖了它？改了 `login()` 会影响什么？

### 整体架构

```
Git Repo ──► Tree-sitter Parser ──► SQLite Graph (nodes + edges)
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
              Blast Radius        Community Det.       Semantic Search
              (调用链追踪)        (Leiden 聚类)        (向量嵌入)
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        ▼
                              MCP Server (30 tools)
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
              Claude Code          Cursor            Windsurf / Zed
              Codex                Gemini CLI        Copilot / ...
```

### 四大技术支柱

| 支柱 | 技术 | 核心价值 |
|------|------|---------|
| **Tree-sitter AST 解析** | 30+ 语言原生解析器 + Jupyter 支持 | 结构化提取函数/类/调用/导入/继承 |
| **GraphRAG 知识图谱** | SQLite + NetworkX + Leiden 社区检测 | 调用链追踪 + 爆炸半径 + 架构分析 |
| **MCP 协议支持** | 30 工具 + 5 Prompt 模板 + 12+ 平台自动安装 | 任何 MCP 客户端即插即用 |
| **增量更新引擎** | SHA-256 哈希 + 依赖反查 + 仅重解析变更文件 | 2900 文件项目 < 2 秒完成增量索引 |

---

## 🛠️ HOW — 四大核心能力实现方式

### 1. Tree-sitter AST 解析（parser.py · 283KB · 6850 行）

**一句话：** 30+ 语言统一解析成 `NodeInfo`（节点）+ `EdgeInfo`（关系），树查询 + 启发式回退双路径。

```python
# 核心解析流程
EXTENSION_TO_LANGUAGE = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".go": "go", ".rs": "rust", ".java": "java",
    ".cpp": "cpp", ".c": "c", ".cs": "c_sharp",
    ".rb": "ruby", ".kt": "kotlin", ".swift": "swift",
    ".php": "php", ".scala": "scala", ".sol": "solidity",
    ".dart": "dart", ".r": "r", ".pl": "perl",
    ".lua": "lua", ".m": "objc", ".sh": "bash",
    ".ex": "elixir", ".zig": "zig", ".ps1": "powershell",
    ".jl": "julia", ".vue": "vue", ".svelte": "svelte",
    ".astro": "astro", ".gd": "gdscript", ".nix": "nix",
    ".v": "verilog", ".sv": "systemverilog", ".sql": "sql",
    ".ipynb": "jupyter", ".xs": "perl_xs",
    # 30+ 扩展名映射
}

# 节点类型映射（每种语言独立维护）
_CLASS_TYPES = {"python": ["class_definition"], "javascript": ["class_declaration"], ...}
_FUNCTION_TYPES = {"python": ["function_definition"], "javascript": ["function_declaration", "arrow_function"], ...}
_IMPORT_TYPES = {"python": ["import_statement", "import_from_statement"], ...}
_CALL_TYPES = {"python": ["call"], "javascript": ["call_expression"], ...}
```

**关键机制：**
- **Tree-sitter 为主，回退为辅**：优先用 tree-sitter 对应语言解析器，语言不支持时降级为启发式正则/文本行分析
- **通用 `NodeInfo` 格式**：所有语言解析结果统一为 `{kind, name, qualified_name, file_path, line_start, line_end, language, parent_name, params, return_type, modifiers, is_test}`
- **边类型**：`CALLS` / `IMPORTS_FROM` / `INHERITS` / `IMPLEMENTS` / `CONTAINS` / `TESTED_BY` / `DEPENDS_ON` / `REFERENCES` — 8 种关系覆盖全部代码语义
- **并行解析**：默认多进程并行解析全部文件（`CRG_SERIAL_PARSE=1` 可回退串行调试模式）
- **Jupyter 支持**：`.ipynb` 文件先提取 code cells 再送入 Python 解析器

### 2. GraphRAG 知识图谱（graph.py · 51KB + communities.py · 30KB）

**一句话：** SQLite 存储 2 类表（nodes + edges），NetworkX 做内存图计算，Leiden 算法做社区检测。

```sql
-- 图 Schema（SQLite）
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT,        -- File, Class, Function, Type, Test
    name TEXT,
    qualified_name TEXT UNIQUE,
    file_path TEXT,
    line_start INTEGER, line_end INTEGER,
    language TEXT, parent_name TEXT,
    params TEXT, return_type TEXT, modifiers TEXT,
    is_test INTEGER DEFAULT 0,
    file_hash TEXT,    -- SHA-256 增量更新关键
    extra TEXT, updated_at REAL
);

CREATE TABLE edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT,         -- CALLS, IMPORTS_FROM, INHERITS, ...
    source_qualified TEXT, target_qualified TEXT,
    file_path TEXT, line INTEGER,
    confidence REAL DEFAULT 1.0,
    confidence_tier TEXT DEFAULT 'EXTRACTED',  -- EXTRACTED/INFERRED/AMBIGUOUS
    extra TEXT, updated_at REAL
);
```

**核心图算法：**

| 算法 | 实现 | 用途 |
|------|------|------|
| **BFS/DFS 遍历** | NetworkX | 调用链追踪、爆炸半径计算 |
| **Leiden 社区检测** | igraph (`[communities]` 可选依赖) | 代码模块自动聚类、架构可视化 |
| **Betweenness Centrality** | NetworkX | 桥接节点检测、架构瓶颈识别 |
| **度中心性** | NetworkX | Hub 节点发现（最常被调用的函数） |
| **惊讶度评分** | 自研 | 跨社区/跨语言的意外耦合检测 |
| **知识缺口分析** | 自研 | 孤立节点、未测试热点、薄弱社区 |

**边置信度三级体系：**
- `EXTRACTED`（1.0）：直接从 AST 提取（如 `import os` → IMPORTS_FROM）
- `INFERRED`（0.5–0.9）：启发式推断（如相同前缀的函数调用）
- `AMBIGUOUS`（<0.5）：模糊匹配（如动态调用、反射）

**爆炸半径（Blast Radius）：**
```
变更文件 ─► 图反查（谁依赖了变更的符号？）
           ├── 直接调用者（CALLS 入边）
           ├── 子类（INHERITS 反向）
           ├── 导入者（IMPORTS_FROM 反向）
           └── 相关测试（TESTED_BY 反向）
         → 最小审查文件集（通常 ≤ 15 个文件）
```

### 3. MCP 协议支持（main.py · 38KB + tools/ 目录 · 12 个工具模块）

**一句话：** 30 个 MCP 工具 + 5 个 Prompt 模板 + 12+ 平台自动安装 + Token Savings 面板。

**30 个 MCP 工具分类：**

```python
# 构建与维护（3）
build_or_update_graph_tool       # 构建/增量更新图谱
run_postprocess_tool             # 重新运行后处理（流检测、社区检测、FTS索引）
embed_graph_tool                 # 计算向量嵌入

# 上下文与审查（4）
get_minimal_context_tool         # 超精简上下文（~100 token）
get_impact_radius_tool           # 变更文件爆炸半径
get_review_context_tool          # Token 优化审查上下文 + 结构摘要
detect_changes_tool              # 风险评分变更影响分析

# 图查询（3）
query_graph_tool                 # 调用者/被调用者/测试/导入/继承查询
traverse_graph_tool              # BFS/DFS 遍历（可配深度+token 预算）
semantic_search_nodes_tool       # 名字/语义搜索代码实体

# 架构分析（8）
list_graph_stats_tool            # 图大小和健康状态
get_architecture_overview_tool   # 基于社区结构的架构总览
get_hub_nodes_tool               # 最连接节点（架构热点）
get_bridge_nodes_tool            # 瓶颈节点（betweenness centrality）
get_knowledge_gaps_tool          # 结构弱点和未测试热点
get_surprising_connections_tool  # 意外跨社区耦合
get_suggested_questions_tool     # 从分析中自动生成审查问题
list_communities_tool / get_community_tool  # 社区列表/详情

# 执行流（3）
list_flows_tool / get_flow_tool / get_affected_flows_tool

# 重构（2）
refactor_tool / apply_refactor_tool

# Wiki（2）
generate_wiki_tool / get_wiki_page_tool

# 多仓库（2）
list_repos_tool / cross_repo_search_tool

# 辅助（3）
get_docs_section_tool / find_large_functions_tool / ...
```

**5 个 MCP Prompt 模板：**
- `review_changes` — 变更审查工作流
- `architecture_map` — 架构图谱生成
- `debug_issue` — 调试问题定位
- `onboard_developer` — 新人上手引导
- `pre_merge_check` — 合并前检查清单

**自动安装机制（`code-review-graph install`）：**

```
检测已安装平台 ─► 写入对应 MCP 配置 ─► 注入图感知指令到平台 rules
    │
    ├── Claude Code:   ~/.claude.json
    ├── Codex:         ~/.codex/config.yml
    ├── Cursor:        ~/.cursor/mcp.json
    ├── Windsurf:      ~/.windsurf/mcp.json
    ├── Zed:           ~/.zed/settings.json
    ├── Continue:      ~/.continue/config.json
    ├── OpenCode:      opencode.json
    ├── Antigravity:   agent.json
    ├── Gemini CLI:    ~/.gemini/settings.json
    ├── Qwen/Qoder/Kiro: 各平台配置路径
    └── GitHub Copilot: VS Code settings.json + CLI config
```

**Token Savings 面板：**

```text
┌─────────────────────── Token Savings ────────────────────────┐
│ Full context would be:     12,921 tokens                     │
│ Graph context used:           762 tokens                     │
│ Saved:                     12,159 tokens (~94%)              │
│ Breakdown: Functions 244 · Tests 191 · Risk 244 · Other 83   │
└──────────────────────────────────────────────────────────────┘
```

- `detect-changes --brief`：只读模式，1 秒出结果
- `update --brief`：先刷新图再分析，5 秒
- `--verify`：用 tiktoken 交叉验证，误差 < 1%
- context_savings 元数据自动附带在 MCP JSON 响应中

### 4. 增量更新机制（incremental.py · 44KB）

**一句话：** 文件保存/commit → SHA-256 diff → 依赖反查 → 仅重解析变更文件 → < 2 秒完成。

```python
# 增量更新核心流程
def incremental_update(repo_path):
    # 1. 检测变更文件（git diff 或 watch 事件）
    changed_files = detect_changed_files()
    
    # 2. SHA-256 哈希比对 — 只处理真正变更的文件
    truly_changed = [
        f for f in changed_files
        if sha256(f) != graph.get_file_hash(f)
    ]
    
    # 3. 依赖反查 — 找到所有受影响节点
    affected_nodes = set()
    for f in truly_changed:
        old_nodes = graph.get_nodes_by_file(f)
        dependent_nodes = graph.reverse_lookup(old_nodes)
        affected_nodes.update(dependent_nodes)
    
    # 4. 精准重解析 — 只解析变更文件
    new_nodes, new_edges = parse_files(truly_changed)
    
    # 5. 原子更新 — 替换旧数据
    graph.replace_nodes(old_nodes, new_nodes)
    
    # 6. 2900 文件项目全流程 < 2 秒
```

**增量更新触发方式：**

| 方式 | 触发时机 | 适用场景 |
|------|---------|---------|
| **Watch 模式** | 文件保存时（文件系统事件） | 开发过程中自动保持图谱更新 |
| **Platform Hooks** | 平台特定事件（保存/切换文件） | Cursor/Windsurf 等支持 hook 的编辑器 |
| **Git Hooks** | commit/post-merge/rebase | 配合版本控制自动更新 |
| **Daemon 模式** | 后台持续文件监控 | 不支持 hook 的编辑器（如 Cursor） |
| **手动 CLI** | `code-review-graph update` | 需要时手动触发 |

**Daemon 架构（daemon.py · 33KB）：**
- `crg-daemon`：独立守护进程，监控多仓库
- 每仓库独立子进程 watcher
- 30 秒健康检查 + 自动重启死进程
- TOML 配置文件（`~/.code-review-graph/watch.toml`）
- 热加载配置变更

---

## 🔄 APPLICATION — Hermes 进化映射

### 关联现有能力

- **关联技能：** [[ai-commander-system]], [[claude-obsidian-architecture]], [[codegraphcontext-mcp-tools]]
- **关联概念：** [[harness-engineering]], [[nexus-dual-engine]], [[token-smart-pipeline]]

### 直接嫁接方案

| code-review-graph 能力 | Hermes 改造 | 实现路径 |
|---|---|---|
| Tree-sitter 多语言解析 | 用 Python `ast` + `tree-sitter` 解析 staged files | 轻量版，专注 Python/TypeScript/Go |
| SQLite 图存储 | 复用 Hermes 本地 SQLite，追加 nodes/edges 表 | 与现有 memory/memories 架构统一 |
| 爆炸半径分析 | pre-commit verifier：变更→影响范围→必读文件列表 | 图查询 API，替代全文 grep |
| 增量 SHA-256 更新 | watch 模式 + 提交前自动刷新 | Hermes cron/trigger 集成 |
| Token Savings 面板 | 在 code review 输出中展示节省 token | CLI 面板或 Hermes response 嵌入 |
| MCP 30 工具 | 抽取 5–8 个核心工具作为 Hermes MCP 插件 | `get_impact_radius` + `query_graph` + `detect_changes` |
| Daemon 多仓库监控 | Hermes 后台 cron 任务 | 轻量版：单仓库 watch 即可 |
| Leiden 社区检测 | 架构分析报告自动生成 | 可选：`[communities]` 依赖 igraph |

### 三阶段落地路线

**Phase 1：最小可用（1–2 天）**
```python
# 仅 Python + SQLite + 调用关系
# 核心：parser(ast) → graph(sqlite) → blast_radius(query)
# 产出：pre-commit verifier 知道"这个 commit 改了 login()，需要重点看 auth.py, session.py, test_auth.py"
```

**Phase 2：语言扩展 + 审查增强（3–5 天）**
```python
# 加入 tree-sitter-{typescript,go,rust}
# 加入社区检测（optional）
# 加入 Semantic Search（sentence-transformers）
# 产出：多语言项目审查 + 架构热点识别
```

**Phase 3：MCP 集成（1–2 天）**
```python
# 暴露 5–8 个核心 MCP 工具
# 写出 Hermes MCP plugin
# 与 Claude Code / Cursor 联动
```

---

## 📊 基准数据总览

| 仓库 | 文件数 | 节点数 | 边数 | Token 压缩比 | 影响召回率 | 平均 F1 |
|------|--------|--------|------|-------------|-----------|---------|
| fastapi | 1,122 | 6,285 | 27,117 | **528x** | 100% | 0.834 |
| code-review-graph | ~500 | — | — | **93x** | 100% | 0.734 |
| gin | 99 | 1,286 | 16,762 | **92x** | 100% | 0.609 |
| flask | 83 | 1,446 | 7,974 | **71x** | 100% | 0.628 |
| express | 141 | 1,910 | 17,553 | **41x** | 100% | 0.667 |
| httpx | 60 | 1,253 | 7,896 | **38x** | 100% | 0.864 |

> 全部 13 个评估 commit，影响召回率 **100%**。不支持的小语种/非标准文件自动跳过，不会误报。

---

## 🪵 飞轮日志

### 2026-05-31 | 第二轮飞轮拆解

- **数据来源：** GitHub API（仓库元数据 + README）+ graph.py 源码（API 获取）+ PyPI 页面
- **拆解深度：** 四大核心能力（Tree-sitter AST / GraphRAG 知识图谱 / MCP 30 工具 / 增量更新）完整分析
- **关键发现：**
  1. **parser.py 达 283KB**（6,850 行），是项目最大的单一文件，承载 30+ 语言的 AST 解析映射
  2. **增量更新 < 2 秒** 的关键是 SHA-256 哈希反查 + 仅重解析变更文件
  3. **12+ 平台自动安装** 策略极聪明：检测已安装编辑器 → 写对应 MCP 配置 → 注入图感知指令
  4. **爆炸半径 100% 召回** 是保守策略：宁可多报 5 个文件，也不漏掉一个依赖
  5. **Token Savings 面板** 是 AI 编码工具中最直观的 ROI 展示——让用户看到省了多少 token
  6. **三个置信度等级**（EXTRACTED/INFERRED/AMBIGUOUS）是值得借鉴的边质量管理方式
  7. **Daemon 模式** 解决了"不支持 hook 的编辑器也能自动更新图谱"的兼容性问题
- **能力审计结论：** 这是目前代码图谱领域最成熟的 MCP 工具，完美填补了 [[codegraphcontext-mcp-tools]] 缺乏的结构化调用链分析能力，是 Hermes pre-commit verifier 的**最佳参考架构**
- **写入路径：** `/Users/apple/nexus-knowledge/concepts/code-review-graph.md`
