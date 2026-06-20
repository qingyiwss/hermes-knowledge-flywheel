# Chrome 浏览器方案 — 完整知识库

> 日期: 2026-06-02 | 环境: macOS 10.15.7 | 代理: ClashX + CordCloud

---

## 一、最终可用方案

### 方案 A: 真实 Chrome CDP 桥接（⭐ 推荐）

**原理**: 用你本地真实 Chrome + Playwright CDP 连上去操控。Google 看到你自己浏览器的指纹和 cookie，`navigator.webdriver = False`，和人手动搜一样。

**桥接脚本**: `~/.local/bin/chrome-bridge.py`

```bash
chrome-bridge.py search "关键词"      # Google 搜索（英文优先）
chrome-bridge.py navigate "网址"      # 打开网页
chrome-bridge.py snapshot             # 页面文本
chrome-bridge.py screenshot           # 截图 → /tmp/chrome-shot.png
chrome-bridge.py status               # 检查状态
chrome-bridge.py stop|start           # 启停
```

**启动方式**（Chrome 必须带 CDP 参数）:
```bash
open -a "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --disable-blink-features=AutomationControlled
```

**依赖**: `pip install playwright`（已在 `~/.cloakbrowser-venv`），Chrome 128.0.6613。

**限制**: 只能是 GUI 模式（headless 不行，Google 会检测）。如果 Chrome 窗口干扰，可以最小化但不关闭。

### 方案 B: Hermes headless 浏览器 + `--disable-ipv6`

**配置** (`~/.hermes/.env`):
```bash
AGENT_BROWSER_EXECUTABLE_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
AGENT_BROWSER_ARGS=--no-sandbox,--proxy-server=http://127.0.0.1:7890,--disable-ipv6
```

**适用**: GitHub（完美）、国内站（完美）、Google 首页（通过）、Google 搜索（看运气，需配合非 Tor 节点）

### 方案 C: GitHub API（零依赖搜索代码）

```bash
curl -x http://127.0.0.1:7890 -s \
  "https://api.github.com/search/repositories?q=关键词&sort=stars" \
  -H "Accept: application/json"
```

免费 60 次/小时，搜代码/仓库 100% 可靠。

---

## 二、已验证结果

| 站点 | Chrome 桥接 | headless Chrome | 终端 curl | GitHub API |
|------|------------|----------------|-----------|------------|
| Google 搜索 | ✅ | ❌ CAPTCHA | ❌ 需 JS | — |
| GitHub | ✅ | ✅ | ✅ 200 | ✅ |
| 百度/国内 | ✅ | ✅ | ✅ | — |
| Stack Overflow | ✅ | ⚠️ 超时 | ✅ 302 | — |
| Cloudflare 站 | ✅ | ❌ | ❌ | — |

---

## 三、踩过的坑

### 坑1: IPv6 泄露
Google CAPTCHA 页面显示 IPv6 `2407:cdc0:...` 而非代理 IPv4。Chrome 的 `--proxy-server` 不覆盖 IPv6。**修复**: `--disable-ipv6`。

### 坑2: CordCloud 出口 IP 是 Tor 节点
当前 IP `185.220.238.37` 被 Google/Cloudflare 标记。切换不同节点无效——所有节点共享同一出口。**根因，无法修复**，只能绕过。这就是为什么需要方案 A（真 Chrome 有登录态能绕过）。

### 坑3: Gateway 重启后 zombie agent-browser 进程
旧 session 的 `agent-browser-darwin-x64` 不随 gateway 退出清理，阻塞新请求。**诊断**: `ps aux | grep agent-browser-darwin-x64`。**修复**: `pkill -9 -f agent-browser-darwin-x64`。

### 坑4: CloakBrowser 不支持 macOS Catalina
`AVFAudio.framework` 缺失（需要 macOS 11+）。0.1.x 无 macOS 二进制。**不可用**。

### 坑5: undetected-chromedriver 间歇性
JS 级 patch 生效（`navigator.webdriver = false`），但 Google 网络层检测 IP，间歇 CAPTCHA。**已弃用**。

### 坑6: Chrome 被 headless 实例锁住
本地 Chrome 打不开 → headless Chrome 占着进程。**修复**: `pkill -9 -f "Google Chrome"`。

---

## 四、搜索引擎替代测试（全部不可用）

| 引擎 | 结果 | 原因 |
|------|------|------|
| StartPage | ❌ 被封 | Tor IP |
| DuckDuckGo | ❌ 被墙 | DNS 污染 |
| Bing 国际版 | ❌ 重定向 cn.bing | 自动识别中国 IP |
| SearXNG 公共实例 | ❌ 全挂 | 被墙/限流 |
| Brave Search API | ⚠️ 需注册 | 免费 2000次/月 |
| Google 纯文本 | ❌ 需 JS | Tor IP 也会封 |

---

## 五、推荐搜索策略

```
搜代码       → GitHub API（首选，零延迟）
搜英文网页   → chrome-bridge.py search（真 Chrome）
搜中文网页   → chrome-bridge.py search + &hl=en（降低 CAPTCHA 概率）
需 JS 渲染   → chrome-bridge.py navigate
只需静态内容 → 终端 curl -x http://127.0.0.1:7890
```

---

## 六、快速排障

```bash
# 代理活着吗？
lsof -i :7890 | grep LISTEN

# Chrome CDP 可用吗？
chrome-bridge.py status

# zombie agent-browser？
ps aux | grep agent-browser-darwin-x64 | grep -v grep

# 本地 Chrome 打不开？
pkill -9 -f "Google Chrome"
```

---

## 七、文件位置

| 文件 | 用途 |
|------|------|
| `~/.hermes/.env` | Hermes 浏览器配置（含 `--disable-ipv6`） |
| `~/.local/bin/chrome-bridge.py` | 真 Chrome 桥接脚本 |
| `~/.cloakbrowser-venv/` | Playwright/undetected-chromedriver 环境 |
| `/tmp/chromedriver-mac-x64/chromedriver` | 手动下载的 ChromeDriver 128 |
| `~/.config/clash/config.yaml` | ClashX 配置（CordCloud 订阅） |
