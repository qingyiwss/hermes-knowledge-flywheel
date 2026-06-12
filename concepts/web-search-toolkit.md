---
id: 20260601-web-search-toolkit
title: Web搜索能力升级 — 多引擎搜索器 + 引擎专用解析器
tags: [web-scraping, search, toolkit, flywheel, 自研]
date_created: 2026-06-01
confidence: high
---

## 🎯 WHAT — 做什么

把散落在各次 `execute_code` 里的搜索代码，固化为一份可复用的搜索器。支持 4 个搜索引擎 + GitHub API。

## 🛠️ HOW — 核心代码

```python
# ~/game-knowledge-flywheel/scripts/searcher.py
import urllib.request, urllib.parse, ssl, re, json

class Searcher:
    """多引擎搜索器 — 免代理，HTTPS直连"""
    
    def __init__(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False  # 国内CDN证书链常断
        self.ctx.verify_mode = ssl.CERT_NONE
        self.ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    
    def _get(self, url):
        req = urllib.request.Request(url, headers={'User-Agent': self.ua})
        resp = urllib.request.urlopen(req, timeout=10, context=self.ctx)
        return resp.read().decode('utf-8', errors='ignore')
    
    def bing(self, query, n=10):
        """Bing搜索 — 中英文混合最佳"""
        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&count={n}"
        html = self._get(url)
        results = re.findall(
            r'<h2[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            html, re.DOTALL
        )
        return [{'title': re.sub(r'<[^>]+>','',t).strip(), 'url': u}
                for u, t in results[:n]]
    
    def baidu(self, query, n=10):
        """百度搜索 — 中文资料"""
        url = f"https://www.baidu.com/s?wd={urllib.parse.quote(query)}"
        html = self._get(url)
        # 百度h3标签
        results = re.findall(
            r'<h3[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            html, re.DOTALL
        )
        return [{'title': re.sub(r'<[^>]+>','',t).strip(), 'url': u}
                for u, t in results[:n]]
    
    def duckduckgo(self, query, n=10):
        """DuckDuckGo Lite — 简洁HTML，不易反爬"""
        url = f"https://lite.duckduckgo.com/lite/?q={urllib.parse.quote(query)}"
        html = self._get(url)
        results = re.findall(
            r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>',
            html, re.DOTALL
        )
        return [{'title': re.sub(r'<[^>]+>','',t).strip(), 'url': u}
                for u, t in results[:n] if 'duckduckgo.com' not in u]
    
    def github(self, query, n=10, sort='stars'):
        """GitHub仓库搜索"""
        q = urllib.parse.quote(query)
        url = f"https://api.github.com/search/repositories?q={q}&sort={sort}&per_page={n}"
        req = urllib.request.Request(url, headers={
            'User-Agent': self.ua,
            'Accept': 'application/vnd.github+json'
        })
        resp = urllib.request.urlopen(req, timeout=10, context=self.ctx)
        data = json.loads(resp.read())
        return [{'name': i['full_name'], 'stars': i['stargazers_count'],
                 'desc': i.get('description',''), 'url': i['html_url']}
                for i in data.get('items', [])[:n]]
```

## 🔄 使用效果

```python
s = Searcher()

# 中文搜索
s.bing("倚天2 游戏币 价格")  # → 官网/百科/私服列表
s.baidu("倚天2觉醒 挂机 脚本")  # → 贴吧/论坛

# 英文搜索
s.bing("metin2 gold farming per hour")  # → Reddit/论坛

# 代码搜索
s.github("metin2 bot farming mmorpg")  # → GitHub开源自挂脚本
```

## ⚠️ 已知局限

| 局限 | 原因 | 缓解 |
|------|------|------|
| 中文URL需编码 | Python ascii限制 | `urllib.parse.quote()` |
| 百度经常0结果 | 反爬升级/HTML结构变 | 备用Bing |
| Bing结果区域偏 | 国内IP → 中文结果优先 | 英中分开搜 |
| Google被代理阻断 | ClashX不支持Google | 用DCV替代Google |
| Sogou反爬严 | 验证码拦截 | 避免高频使用 |

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初版 | 2026-06-01 | 固化4引擎搜索器，从execute_code碎片代码提升为复用模块 |
