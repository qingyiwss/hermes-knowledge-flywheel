---
id: 20260529-qodomerge
title: Qodo Merge AI代码审查架构拆解
tags: [skill-learning, automation, agent-upgrade, team-collaboration]
source_url: https://github.com/Codium-ai/pr-agent
date_created: 2026-05-29
last_updated: 2026-05-29
---

## 1. 项目概述

Qodo Merge（原 PR-Agent）是 Codium AI 开源的 AI 驱动代码审查工具，GitHub Stars ~7.5K，Python 实现。它自动对 Pull Request 进行 review、描述、改进建议、问答反思等全流程审查，支持 GitHub/GitLab/Bitbucket 等 5 种 Git 平台，后端可接入 10+ LLM（GPT-4、Claude、DeepSeek 等）。通过 `.pr_agent.toml` 配置文件驱动行为，实现了高度可定制的审查流水线。

## 2. 核心架构拆解

### 2.1 Agent Pipeline 模式

Qodo Merge 采用 **8 个独立子 Agent** 的 Pipeline 架构，各 Agent 职责单一、可自由组合：

| Agent | 职责 | 触发方式 |
|-------|------|----------|
| `review` | 逐行审查 diff，输出问题清单与建议 | 自动/手动 |
| `describe` | 自动生成 PR 描述与变更摘要 | 自动 |
| `improve` | 生成可直接提交的代码改进补丁 | 手动 |
| `ask` | 自由问答，针对 PR 回答任意问题 | 手动 |
| `reflect` | 对历史审查进行反思与复盘 | 手动 |
| `update_changelog` | 根据 diff 自动更新 Changelog | 自动 |
| `similar_issue` | 检索相似历史 issue，避免重复踩坑 | 自动 |
| `add_docs` | 为新增代码自动补充文档 | 手动 |

核心执行链路：`diff → chunk → LLM → publish_review()`。大 diff 被智能切分为 token-safe 的 chunk，逐块送入 LLM 后聚合结果，最终通过 GitProvider 发布评论。

### 2.2 抽象层设计

- **GitProvider 抽象层**：统一封装 GitHub/GitLab/Bitbucket/Azure DevOps/CodeCommit 的 API 差异，上层 Agent 不感知平台细节。
- **AiHandler 抽象层**：适配 OpenAI、Anthropic、DeepSeek、Ollama 等 10+ 后端，支持本地与云端模型自由切换。

### 2.3 配置驱动

`.pr_agent.toml` 集中管理所有行为参数——审查规则、忽略模式、LLM 参数、Agent 开关等。团队可按仓库定制审查策略，实现"配置即文档"。

## 3. 🔄 Hermes 进化映射 (Integration Roadmap)

Qodo Merge 的以下设计模式可直接迁移到 Hermes Agent 体系中：

- **子 Agent 拆分模式**：将 Hermes 单一大模型 Agent 拆为 review/describe/improve 等独立子 Agent，每个子 Agent 有专精的 system prompt 与工具集，通过 [[concepts/agent-orchestration]] 调度协作。这与当前 Hermes 的 skill 机制天然契合——每个子 Agent 封装为一个 skill。

- **配置驱动行为**：借鉴 `.pr_agent.toml` 的配置哲学，为 Hermes 设计 `hermes-rules.yaml`，让团队以声明式方式定义审查规则、忽略范围、模型参数，实现 [[concepts/config-driven-agents]] 的运维模式。

- **Chunk 化处理**：大上下文场景（如长文档、大型代码库）中，采用 diff → chunk → LLM 的分片策略，结合 Hermes 的 context 管理能力，解决 token 窗口限制问题。

- **多平台 Provider 抽象**：Qodo Merge 的 GitProvider 抽象证明"统一接口 + 多后端适配"模式可落地。Hermes 可以此为指导，设计统一的 ChatProvider / StorageProvider 抽象层，降低平台迁移成本。

- **自动化流水线**：从 review → improve → add_docs 的端到端自动化思路，可用于构建 Hermes 的 [[concepts/ci-agent-pipeline]]——代码提交后自动 review、自动生成文档、自动更新变更日志，形成完整的 AI 辅助开发闭环。
