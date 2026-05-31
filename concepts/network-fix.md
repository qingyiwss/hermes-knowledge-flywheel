---
id: 20260531-network-fix
title: 终端网络修复 — 代理环境变量 + GitHub CDN 直连
tags: [network, proxy, clashx, terminal, fix]
date_created: 2026-05-31
confidence: high
---

## 🎯 WHAT — 问题

飞轮执行中频繁遇到 `raw.githubusercontent.com` 连接超时、子Agent API 404、curl 不走代理。

## 🔍 根因分析

| 层面 | 问题 | 修复 |
|------|------|------|
| 终端 | `http_proxy`/`https_proxy` 均为空 | 写入 `.bash_profile` |
| ClashX 节点 | 某些节点连 GitHub CDN 时 SSL 握手失败 | 规则加 DIRECT |
| DNS | `fake-ip` 模式没问题 | 保持不变 |

## 🛠️ 已落地修复

### 1. .bash_profile 代理持久化

```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY=$http_proxy
export HTTPS_PROXY=$https_proxy
export no_proxy=localhost,127.0.0.1,.cn,api.github.com,raw.githubusercontent.com,.github.io
export NO_PROXY=$no_proxy
```

### 2. ClashX 规则：GitHub CDN 直连

```yaml
- DOMAIN-SUFFIX,raw.githubusercontent.com,DIRECT
- DOMAIN-SUFFIX,github.io,DIRECT
```

### 3. 知识沉淀

- 更新 `macos-toolchain` skill（§2.4 + §2.5）
- 本页 Wiki

## ✅ 验证结果

| 目标 | 方式 | 状态 |
|------|------|------|
| raw.githubusercontent.com | 直连 (DIRECT) | ✅ HTTP 301 |
| www.google.com | 走代理 (PROXY) | ✅ HTTP 200 |
| api.github.com | 直连 (no_proxy) | ✅ |

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初始 | 2026-05-31 | 修复终端代理+ClashX规则，双通道验证通过 |
