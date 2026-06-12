---
id: 20260601-direct-data-sources
title: 游戏数据直连源 — 绕过搜索直接拿数据
tags: [web-scraping, game-economics, data-source, flywheel]
date_created: 2026-06-01
confidence: medium
---

## 🎯 WHAT — 数据源矩阵

搜索引擎的问题是：搜到的全是官网+百科，没有实际交易数据。解决方案：**直接访问数据源，不经过搜索。**

## 🛠️ HOW — 数据源清单

### 价格数据（实时交易价格）

| 平台 | URL模式 | 数据格式 | 状态 |
|------|---------|----------|------|
| DD373 | `dd373.com/s-yt2-*.html` | 表格HTML | 🔴需登录 |
| 5173 | `5173.com/game/yt2` | 列表HTML | 🔴JS渲染 |
| G2G | `g2g.com/categories/metin2-gold` | 卡片HTML | 🔴JS渲染 |

**方案：** 这些平台都有反爬（JS渲染+登录墙），浏览器自动化是唯一出路。但 Hermes 的 `browser` 工具可以渲染 JS。

### 论坛数据（玩家讨论、价格参考）

| 来源 | URL | 数据 |
|------|-----|------|
| 贴吧 | `tieba.baidu.com/f?kw=倚天2觉醒` | 玩家晒收益/交易帖 |
| Reddit | `reddit.com/r/Metin2` | 国际服务器经济讨论 |
| Metin2 Board | `board.metin2.fr` 等 | 官方论坛交易板块 |
| ElitePVPers | `elitepvpers.com/forum/metin2` | 最大英文私服交易论坛 |

**访问方式：**
- 贴吧 → `browser` 渲染（AJAX加载）
- Reddit → `reddit.com/r/Metin2/.json` 直取 JSON API
- ElitePVPers → 直接用 `browser` 或 curl

### 私服数据

| 来源 | URL | 数据 |
|------|-----|------|
| Metin2.GG | `metin2.gg/en/metin2-server-list` | 活跃服务器列表+在线人数 |
| XtremeTop100 | `xtremetop100.com/metin2` | 服务器排名+投票数 |
| GTop100 | `gtop100.com/metin2` | 同上 |

**访问方式：** 这些是静态HTML（服务端渲染），`curl` 直抓即可。

### 开源代码

| GitHub搜索词 | 收获 |
|-------------|------|
| `metin2 bot farming` | 自动打怪/钓鱼脚本 |
| `metin2 private server source` | 服务端源码（了解掉落率/经济模型） |
| `metin2 hack gold` | 内存修改工具（风险高） |

**访问方式：** `Searcher.github("metin2 bot farming")`

## 📊 实战优先级

```
P0: Reddit JSON API     ← 免登录/免渲染/结构化数据
P1: Metin2.GG 服务器列表  ← 静态HTML
P2: ElitePVPers论坛      ← browser渲染
P3: 贴吧                ← browser渲染(需处理反爬)
```

### Reddit Metin2 经济数据获取

```python
import urllib.request, json

url = "https://www.reddit.com/r/Metin2/search.json?q=gold+farming+price&sort=new&limit=10"
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (compatible; Metin2Bot/1.0)'
})
data = json.loads(urllib.request.urlopen(req).read())
for post in data['data']['children']:
    p = post['data']
    print(f"{p['title']}")
    print(f"  {p['selftext'][:200]}")
```

### 私服列表抓取

```python
# metin2.gg 是服务端渲染HTML，curl直抓即可
url = "https://metin2.gg/en/metin2-server-list"
html = Searcher()._get(url)
# 提取服务器名+在线人数
import re
servers = re.findall(r'<td[^>]*>(.*?)</td>.*?<td[^>]*>(\d+)</td>', html, re.DOTALL)
```

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初始 | 2026-06-01 | 分类数据源矩阵 + Reddit JSON API + 私服列表抓取策略 |
