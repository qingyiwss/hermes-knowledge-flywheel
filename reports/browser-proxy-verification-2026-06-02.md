# Chrome Agent 浏览器代理 — 经验总结与方案文档

> 日期: 2026-06-02 | 环境: macOS 10.15.7 | 代理: ClashX + CordCloud

---

## 一、最终配置方案

### .env 关键配置（`~/.hermes/.env`）

```bash
AGENT_BROWSER_EXECUTABLE_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
AGENT_BROWSER_ARGS=--no-sandbox,--proxy-server=http://127.0.0.1:7890
BROWSER_SESSION_TIMEOUT=300
BROWSER_INACTIVITY_TIMEOUT=120
```

### 生效方式
修改 `.env` 后 **必须重启 Gateway**（`hermes gateway restart`），否则旧 session 的 agent-browser 进程不会加载新配置。

---

## 二、验证矩阵

| 站点 | 浏览器 | 终端 curl | 备注 |
|------|--------|-----------|------|
| **百度** | ✅ 秒开 | — | 国内直连 |
| **GitHub** | ✅ 完整 | ✅ 200 | 无 CAPTCHA，DOM完整 |
| **httpbin.org/ip** | ✅ 代理生效 | ✅ 185.220.238.37 | 确认走代理 |
| **Google** | ❌ CAPTCHA | ✅ 200 | Tor节点被封 + IPv6泄露 |
| **DuckDuckGo** | ❌ 超时 | ✅ 200 | 被墙 |
| **Stack Overflow** | ❌ 超时 | ✅ 302 | Cloudflare拦截 |
| **elitepvpers** | — | ❌ 403 | Cloudflare拦截 |
| **api.ip.sb** | ❌ 超时 | ✅ 200 | 浏览器挂起 |
| **Bing** | ⚠️ 国内版 | — | 自动重定向cn.bing.com |
| **news.ycombinator.com** | — | ✅ 405 | curl正常 |

### 可用站点清单
- ✅ GitHub / GitHub Raw / Gist — 完全可用
- ✅ httpbin.org — IP验证可用
- ✅ 所有国内站（百度/B站/知乎/CSDN）— 直连可用
- ⚠️ Google — 英文有时通，但大概率 CAPTCHA
- ❌ Stack Overflow / Cloudflare 站点 — 不可用
- ❌ DuckDuckGo — 被墙

---

## 三、踩过的坑

### 坑1: Gateway 重启 → zombie agent-browser 进程 🔴 高危

**现象**: Gateway 重启后所有 `browser_navigate` 60秒超时，连百度都不通。

**根因**: 旧 session 的 `agent-browser-darwin-x64` 进程未随 gateway 退出而清理，占据 Chrome 的控制通道，新请求被阻塞。

**诊断命令**:
```bash
ps aux | grep 'agent-browser-darwin-x64' | grep -v grep
```

**修复**:
```bash
pkill -9 -f "agent-browser-darwin-x64"
```

**预防**: 将来 gateway 重启脚本应加入 `pre_stop` hook 自动清理。

---

### 坑2: 代理节点是 Tor 出口节点 🔴 致命

**现象**: Google 永久 CAPTCHA，Cloudflare 站点全部 403/超时。

**根因**: CordCloud 返回的节点 `185.220.238.37` 是 Tor 出口节点，被所有反爬系统标记为恶意 IP。

**验证**:
```bash
curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip
# → "origin": "185.220.238.37"
```

**备选方案**:
1. ClashX 手动切换到非 Tor 节点（台湾/日本/新加坡住宅 IP）
2. 添加规则 `DOMAIN-SUFFIX,google.com,🇹🇼台湾` 强制指定节点
3. 升级 CordCloud 套餐到住宅 IP 线路

---

### 坑3: IPv6 泄露 🟡 中等

**现象**: Google CAPTCHA 页面显示 IPv6 地址 `2407:cdc0:...`，而非代理 IPv4 `185.220.238.37`。

**根因**: Chrome 的 `--proxy-server` 参数只代理 IPv4 流量，IPv6 直连泄露真实地址。

**修复方案**:
```bash
# 方案A: 禁用 Chrome IPv6（推荐）
AGENT_BROWSER_ARGS=--no-sandbox,--proxy-server=http://127.0.0.1:7890,--disable-ipv6

# 方案B: 系统级禁用 IPv6（影响范围大）
sudo networksetup -setv6off Wi-Fi
```

---

### 坑4: DuckDuckGo 被墙 🟡 中等

浏览器和 curl 都无法访问，不是代理问题——DDG 自身在中国大陆被 DNS 污染 + IP 封锁。

**替代方案**:
- **Bing 国际版**: `https://www.bing.com/?cc=us` （需手动切非 cn.bing.com）
- **Google + `&hl=en`**: 英文搜索偶尔能过，但不能依赖
- **SearXNG**: 自建聚合搜索，不走单一搜索引擎

---

### 坑5: Google CAPTCHA 的中文触发 🟢 已解

搜中文时 CAPTCHA 概率远高于英文。因为中文搜索模式更接近爬虫行为特征。

**缓解**: 优先英文关键词 + `&hl=en` 参数。

---

## 四、终端 curl vs 浏览器对比

| 特性 | 终端 curl | 浏览器 (Chrome headless) |
|------|-----------|------------------------|
| 代理方式 | `-x http://127.0.0.1:7890` | `--proxy-server=http://...` |
| IPv6泄露 | ❌ 无（curl 默认IPv4） | ⚠️ 存在 |
| CAPTCHA | 几乎不触发 | 频繁触发（Tor节点） |
| JS渲染 | ❌ 无 | ✅ 完整 |
| 反爬对抗 | 弱 | 强（Stealth features） |
| 速度 | 0.3-1s | 2-60s（取决于站点） |
| 适用场景 | API/文档/JSON | 需要JS/表单/CAPTCHA页面 |

**黄金法则**: 能 curl 的不用浏览器。只有需要 JS 渲染、表单交互、绕过 Cloudflare JS Challenge 时用 browser。

---

## 五、推荐的搜索策略（当前环境）

```
优先级1: GitHub site:搜索
  → browser_navigate "https://github.com/search?q=Metin2+bot&type=repositories"

优先级2: Google 英文（碰运气）
  → browser_navigate "https://www.google.com/search?q=...&hl=en&num=10"

优先级3: Bing 国际版
  → browser_navigate "https://www.bing.com/search?q=...&cc=us"

优先级4: 直接 curl API
  → terminal "curl -x http://127.0.0.1:7890 -s https://api.github.com/search/repositories?q=..."
```

---

## 六、待解决问题

1. **[高优]** 切换到非 Tor 代理节点 — 这是 Google/Cloudflare CAPTCHA 的根因
2. **[中优]** 加 `--disable-ipv6` 到 `AGENT_BROWSER_ARGS` — 堵住 IPv6 泄露
3. **[低优]** Gateway 重启脚本加 `pkill agent-browser` — 防止 zombie 进程

---

## 七、快速诊断清单

当浏览器不通时，按顺序排查：

```bash
# 1. 代理活着吗？
lsof -i :7890 | grep LISTEN

# 2. 终端能走代理吗？
curl -x http://127.0.0.1:7890 -sI https://www.google.com | head -1

# 3. 有 zombie agent-browser 吗？
ps aux | grep 'agent-browser-darwin-x64' | grep -v grep

# 4. Chrome 进程在跑吗？
ps aux | grep 'Google Chrome' | grep -v grep | wc -l

# 5. 代理出口 IP 是什么？
curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip
```

---

**结论**: 方案本身正确（`--proxy-server`），真正的问题在代理节点质量（Tor出口）和运维细节（zombie进程清理、IPv6泄露）。终端 curl 完全不受影响——对于不需要 JS 渲染的任务优先用 curl。
