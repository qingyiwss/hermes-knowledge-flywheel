---
id: 20260601-network-diagnostics
title: 网络抓取瓶颈诊断 — 真正的问题不是网络
tags: [network, web-scraping, diagnosis, flywheel]
date_created: 2026-06-01
confidence: high
---

## 🎯 WHAT — 诊断结果

全部 8 个目标的 DNS 解析、TCP 连通、HTTP 返回均正常。之前失败的原因是 **HTML 解析代码写错**，不是网络问题。

### 环境真相

| 层 | 状态 | 说明 |
|----|------|------|
| DNS | ✅ 全通 | google/baidu/bing/sogou/duckduckgo/github/dd373/5173/g2g |
| TCP 443 | ✅ 全通 | curl --noproxy 直连全部 200 |
| ClashX 代理 | ✅ 正常 | :7890 代理 Google 以外目标正常 |
| Python urllib | ✅ 直连可用 | 所有搜索引擎 HTTPS 200 |

### Google 代理阻断

多目标唯一失败的是 Google via proxy。但不需要 Google——Bing/DDG/Baidu/Sogou 全通且免代理。

## 🛠️ 之前的错误分析

| 错误模式 | 原因 | 修复 |
|----------|------|------|
| `sys.stdin.read()` 后 HTML parser 空输出 | curl 输出包含二进制干扰 | 用 Python `urllib.request` 原生请求 |
| Baidu 中文 URL UnicodeEncodeError | URL 含中文字符未编码 | `urllib.parse.quote()` |
| 搜索结果 regex 匹配为空 | 各引擎 HTML 结构不同 | 引擎专用提取器 |
| 0 条结果 | 搜索引擎反爬(User-Agent) | 加 `Mozilla/5.0` UA |

## 📊 可通路径总结

```
Python urllib.request + SSL(context=no_verify)
  ✅ Bing     — 中英文混合搜索最佳
  ✅ Baidu    — 需URL编码中文
  ✅ DuckDuckGo — lite版简单HTML
  ✅ Sogou    — 但容易触发反爬(验证码)
  ✅ GitHub API — 项目搜索，需token防限流
  ✅ httpbin.org — 网络诊断
  ❌ Google   — 被代理阻断
```

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 发现 | 2026-06-01 | DNS/TCP/HTTP全链路诊断，发现真正问题是解析代码而非网络 |
