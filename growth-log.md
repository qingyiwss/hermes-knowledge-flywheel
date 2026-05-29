# 进化日志

> Hermes 知识飞轮每次循环的成长记录。按时间倒序。

## 轮次 0 — 飞轮启动 [2026-05-29]

### 初始化内容
- 建立知识飞轮四阶段循环（扫描→拆解→沉淀→提交）
- 搭建三层指挥系统（Hermes/cc/reasonix + Obsidian Wiki）
- 配置主模型 deepseek-v4-pro + fallback deepseek-v4-flash

### 当前能力评估
| 维度 | 现状 | 短板 |
|------|------|------|
| 任务编排 | ✅ project-commander 6步法 | 缺少动态优先级调整 |
| 代码执行 | ✅ cc (Claude Code) | tmux 交互模式不稳定 |
| 知识管理 | ✅ Obsidian LLM Wiki | 缺少自动关联图谱 |
| 工具分析 | ⚠️ reasonix 可用 | 回测策略种类少 |
| 联网搜索 | ❌ | 无 web_search 工具 |

### 下一步计划
- 本轮扫描方向：AI Agent 编排框架 + CLI 自动化工具 + Prompt 工程
- 优先补齐：联网能力、动态任务调度

---

## 轮次 1 — Harness工程 + 联网能力 [2026-05-29]

### 扫描范围
- 三个方向各取 Top3 仓库，精选 2 个深度拆解

### 拆解成果

| 项目 | ⭐ | 学到的 | 产物 |
|------|-----|--------|------|
| shareAI-lab/learn-claude-code | 63k | Agent = Model + Harness；Harness 五要素；六大核心模式 | [[harness-engineering]] |
| Panniantong/Agent-Reach | 20k | 一键互联网能力；MCP 网关；多平台免费接入 | [[agent-reach-internet]] |

### 核心洞察
1. **我们已有 80% 的 Harness** — project-commander 本质上就是个 Harness，缺少的是"Harness 构建者"思维
2. **联网是最大短板** — Agent Reach 可以直接填补，安装即可用
3. **Context Compaction 待补** — 长会话 token 管理是下一个要解决的问题

### 能力评估更新
| 维度 | 之前 | 之后 |
|------|------|------|
| Harness 意识 | ⚠️ 有结构但无意 | ✅ 明确五要素框架 |
| 联网搜索 | ❌ | ⚠️ 方案已定，待安装 |
| 知识归档 | ✅ | ✅ 两篇深度笔记入 wiki |

### 下一步
- [ ] 安装 Agent Reach，创建 web-search skill
- [ ] 更新 project-commander 加入 Harness 检查表
- [ ] 第二轮扫描方向：Context 管理 + Prompt 优化
