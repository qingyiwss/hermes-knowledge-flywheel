---
id: 20260529-affine
title: AFFiNE 知识协作架构拆解
tags: [skill-learning, automation, agent-upgrade, team-collaboration]
source_url: https://github.com/toeverything/AFFiNE
date_created: 2026-05-29
updated: 2026-05-29
last_updated: 2026-05-29
---

# AFFiNE 知识协作架构拆解

## 一、项目概览

AFFiNE 是一个开源的 **Notion + Miro 替代品**（GitHub ~45K Stars），技术栈为 **TypeScript + Rust**。核心定位是「本地优先 + 实时协作」的知识操作系统。

与 [[notion-architecture]] 的最大区别在于：AFFiNE 不是云端单体的 SaaS，而是**去中心化架构**——数据首先存储在本地，协作时通过 CRDT 增量同步到远端。这意味着即使离线，所有功能仍然可用。

## 二、核心机制：CRDT 驱动的实时同步

AFFiNE 的实时协作不走 OT（Operational Transformation）老路，而是基于 **Yjs CRDT**（Conflict-free Replicated Data Type）。

**工作流程：**

```
用户编辑 → Yjs 生成原子操作 → 本地 SQLite 持久化
    ↕
OctoBase 服务器 → 增量同步 → 其他协作者（无锁合并）
```

1. 每个编辑操作被 Yjs 编码为携带逻辑时钟的原子变更
2. 变更先写入本地 SQLite（毫秒级响应），再异步推送到 [[octobase-server]]
3. 其他客户端收到变更后直接 apply——**不需要冲突解决**，因为 CRDT 的交换律保证所有副本最终一致
4. 离线编辑自动排队，上线后按因果顺序合并，不会丢数据

这条链路的关键收益：**零冲突合并 + 离线编辑无感知恢复**，彻底消除了「冲突副本」的噩梦。

## 三、BlockSuite：可切换视图的块编辑器

[[blocksuite-editor]] 是 AFFiNE 的编辑器内核，也是它区别于纯文本文档协作的杀手锏：

- **所有内容都是 Block**：段落、图片、表格、看板卡片——统一抽象为 Block 节点
- **视图切换**：同一份 Block 数据，可以在文档视图、白板视图、数据库视图中自由切换
- BlockSuite 本身基于 Lit（Web Components）构建，框架无关，可嵌入任意前端项目

这种「数据与视图分离」的设计，让 AFFiNE 在不引入额外同步逻辑的前提下，实现了 Notion 的分层页面 + Miro 的无限画布，本质上把「协作画布」和「结构化文档」统一了。

## 小结

AFFiNE 的架构决策链条非常清晰：**BlockSuite（统一数据模型）→ Yjs CRDT（去中心化同步）→ OctoBase（本地优先服务器）**。三者共同构成了一条从「块级编辑」到「多端实时合并」的完整知识协作流水线。对于需要离线编辑 + 多人实时协作的产品，这条架构路径是目前开源社区最成熟的参考方案。
