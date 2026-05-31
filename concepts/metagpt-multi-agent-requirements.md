---
id: 20260529-metagpt
title: MetaGPT — 多 Agent 需求→软件全流程
tags: [skill-learning, ai-agent, requirements, multi-agent, code-generation]
source_url: https://github.com/FoundationAgents/MetaGPT
date_created: 2026-05-29
updated: 2026-05-29
last_updated: 2026-05-29
---

## 🎯 核心痛点与应用场景

**痛点：** 需求分析和架构设计占软件开发 40% 时间，但 AI 编码工具（Copilot/Cursor）只解决"写代码"环节，前面的需求澄清、系统设计、任务拆解仍靠人。

**MetaGPT 方案：** 模拟一家软件公司的全部角色——产品经理写 PRD → 架构师做设计 → 工程师写代码 → QA 写测试。输入一句话需求，输出完整的文档+代码+测试。

**关键创新：** SOP（标准作业流程）驱动——不是让 Agent 自由对话，而是强制每个角色按固定的半结构化文档模板输出，保证质量一致性。

## 🛠️ 底层原理解析

**角色分工（模拟真实公司）：**
```
User Input: "做一个股票分析系统"
  ↓
ProductManager → PRD.md（竞品分析、用户故事、功能列表）
  ↓
Architect → Design.md（技术栈、API设计、数据流图）
  ↓
Engineer → code/*.py（按PRD逐功能实现）
  ↓
QA → tests/*.py（按用户故事写测试）
```

**核心机制：Message + Role + Environment 三元组**

```python
# 简化版核心循环
class Role:
    def _think(self):
        # 1. 从环境观察最新消息
        # 2. 根据角色身份决定下一步行动
        # 3. 生成结构化输出（文档/代码）

class Environment:
    def publish_message(self, msg):
        # 广播消息给所有角色

# PM 输出格式（必须遵守的模板）
PRD = {
    "Language": "zh-CN",
    "Original Requirements": "...",
    "Product Goals": ["...", "..."],
    "User Stories": [{"story": "...", "acceptance": "..."}],
    "Competitive Analysis": ["..."]
}
```

**SOP 的价值：** 传统 Agent 自由对话容易跑偏，强制输出模板 → 下游角色可靠地消费上游产物 → 全流程可复现。

## 🔄 Hermes 进化映射 (Integration Roadmap)

**对我们的直接影响：**
- **Commander 模式可升级：** 目前 commander 拆解任务靠 prompt 描述，可借鉴 MetaGPT 的 SOP 模板化——定义"代码任务模板""分析任务模板""Wiki 任务模板"
- **cc 的 CLAUDE.md 可要求输出格式：** 类似 PM 的 PRD 模板，要求 cc 输出符合固定 schema 的结果

**具体落地：**
```yaml
# 升级后的任务模板
task_template:
  type: code_review
  sections: [issues_found, severity, fix_suggestion, files_to_modify]
  format: markdown_table
```

**相关笔记：** [[a2a-protocol]]、[[agent-orchestration-patterns]]
