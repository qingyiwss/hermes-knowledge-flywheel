---
title: Claude Bug Bounty — AI驱动的自主渗透测试框架
domain: ai-security
subdomain: bug-bounty-automation
type: concept
created: 2026-05-31
tags:
  - bug-bounty
  - penetration-testing
  - claude-code
  - vulnerability-scanner
  - autonomous-hunting
  - nexus-cc-integration
---

# Claude Bug Bounty — AI 驱动自主渗透测试

> **GitHub**: shuvonsec/claude-bug-bounty | ⭐2,340 | MIT License
> **定位**: Claude Code 插件，将 AI 编程助手转化为专业漏洞赏金猎人
> **核心理念**: 用一个命令取代 10+ 工具 + 手动报告撰写，AI 负责从侦察到报告的完整链路

---

## 一、架构全景

### 1.1 系统组成

```
用户
  │
  ▼
Claude Code（编排层）
  │
  ├── 8 个 AI Agent（专项任务执行）
  ├── 23 个 Slash 命令（快捷入口）
  ├── 9 个 Skill 文件（知识注入）
  └── 50+ 外部工具（扫描执行）
            │
            ▼
       猎杀记忆（跨会话持久化）
```

### 1.2 8 个 AI Agent

| Agent | 职责 | 触发场景 |
|-------|------|----------|
| **recon-agent** | 子域名枚举、存活探测、URL 采集 | `/recon` 命令 |
| **report-writer** | 编写影响优先的专业漏洞报告 | `/report` 命令 |
| **validator** | 7 问门控，在浪费时间前杀死弱发现 | `/validate` 命令 |
| **web3-auditor** | 10 类合约漏洞审计 | `/web3-audit` 命令 |
| **chain-builder** | 发现 A 漏洞 → 找到关联的 B、C 漏洞链 | `/chain` 命令 |
| **autopilot** | 全自主运行完整猎杀循环 | `/autopilot` 命令 |
| **recon-ranker** | 攻击面排序，优先测试高价值目标 | `/surface` 命令 |
| **token-auditor** | Meme 币/代币跑路风险扫描 | `/token-scan` 命令 |

### 1.3 核心 Slash 命令（23 个）

**基础四件套：**
- `/recon target.com` — 子域名+存活+URL+基础扫描
- `/hunt target.com` — 按技术栈选择渗透技术进行漏洞探测
- `/validate` — 7 问门控，写报告前过筛
- `/report` — 生成 H1/Bugcrowd/Intigriti/Immunefi 格式报告

**进阶：**
- `/autopilot target.com` — 全自主模式（--paranoid / --normal / --yolo）
- `/surface target.com` — 攻击面排序
- `/pickup target.com` — 恢复上次会话未测试端点
- `/intel target.com` — CVE 情报 + 已披露报告
- `/chain` — 漏洞链接狩猎（A→B→C）
- `/web3-audit` / `/token-scan` — 合约审计 + 代币扫描

**侦察工具箱（v4.3）：**
- `/scope-aggregate` — 聚合多平台资产范围
- `/secrets-hunt` — 源码/JS 中的泄露凭证
- `/takeover` — 子域名接管检测
- `/cloud-recon` — 公有云资源枚举
- `/param-discover` — 隐藏参数发现
- `/bypass-403` — 403/401 绕过技巧
- `/scan-cves` — 漏洞扫描
- `/arsenal` — 工具清单/安装提示

---

## 二、20 种 Web2 漏洞检测类型

| # | 漏洞类型 | 中文说明 | 典型奖金 |
|---|----------|----------|----------|
| 1 | **IDOR** | 越权访问 — 修改 URL 中的数字访问他人数据 | $500-$5K |
| 2 | **Auth Bypass** | 认证绕过 — 无授权进入账户/管理面板 | $1K-$10K |
| 3 | **XSS** | 跨站脚本 — 注入恶意脚本到页面 | $500-$5K |
| 4 | **SSRF** | 服务端请求伪造 — 让服务器访问内部资源 | $1K-$15K |
| 5 | **Business Logic** | 业务逻辑漏洞 — 利用应用流程设计缺陷 | $500-$10K |
| 6 | **Race Conditions** | 竞态条件 — 并发请求获取双倍奖励 | $500-$5K |
| 7 | **SQL Injection** | SQL 注入 — 通过用户输入操纵数据库 | $1K-$15K |
| 8 | **OAuth/OIDC** | OAuth/OIDC 攻击 — 破坏第三方登录流程 | $500-$5K |
| 9 | **File Upload** | 文件上传 — 上传恶意文件导致代码执行 | $500-$5K |
| 10 | **GraphQL** | GraphQL 攻击 — 认证绕过和数据泄露 | $1K-$10K |
| 11 | **LLM/AI** | AI 功能安全 — Prompt 注入/AI 功能 IDOR | $500-$10K |
| 12 | **API Misconfig** | API 配置错误 — 批量赋值/JWT 攻击/CORS 配置 | $500-$5K |
| 13 | **Account Takeover** | 账户接管 — 完全控制他人账户 | $1K-$20K |
| 14 | **SSTI** | 模板注入 — 模板引擎注入导致代码执行 | $2K-$10K |
| 15 | **Subdomain Takeover** | 子域名接管 — 认领过期子域名 | $200-$5K |
| 16 | **Cloud/Infra** | 云/基础设施 — S3 桶公开/Firebase/K8s | $500-$20K |
| 17 | **HTTP Smuggling** | HTTP 走私 — 前后端服务器解析差异 | $5K-$30K |
| 18 | **Cache Poisoning** | 缓存投毒 — CDN 缓存投毒 | $1K-$10K |
| 19 | **MFA Bypass** | 多因素认证绕过 — 绕过双因素认证 | $1K-$10K |
| 20 | **SAML/SSO** | SAML/SSO 攻击 — 企业单点登录漏洞 | $2K-$20K |

### 10 种 Web3/智能合约漏洞

| # | 漏洞类型 | 中文说明 | 典型奖金 |
|---|----------|----------|----------|
| 1 | **Reentrancy** | 重入攻击 | $10K-$500K |
| 2 | **Oracle Manipulation** | 预言机操纵 | $100K-$2M |
| 3 | **Access Control** | 访问控制缺陷 | $50K-$2M |
| 4 | **Accounting Desync** | 会计不同步 | $50K-$2M |
| 5 | **Flash Loan** | 闪电贷攻击 | $100K-$2M |
| 6 | **Signature Replay** | 签名重放 | $10K-$200K |
| 7 | **ERC4626 Attacks** | ERC4626 vault 攻击 | $50K-$500K |
| 8 | **Off-By-One** | 边界错误 | $10K-$100K |
| 9 | **Incomplete Code Path** | 不完整代码路径 | $50K-$2M |
| 10 | **Proxy/Upgrade** | 代理/升级漏洞 | $50K-$2M |

---

## 三、侦察信息收集体系

### 3.1 侦察引擎 8 阶段流程（recon_engine.sh）

```
Phase 0: 目标类型检测
  → FQDN / IP / CIDR / 域名列表文件
  → CIDR 自动展开并 nmap ping 扫

Phase 1: 子域名枚举
  → subfinder（被动快速）→ amass → assetfinder → Chaos API
  → 合并去重 → 输出 all.txt

Phase 2: DNS 解析
  → dnsx 批量解析 → 获取 A/AAAA/CNAME 记录

Phase 3: 存活探测
  → ProjectDiscovery httpx → 技术指纹识别
  → 返回状态码、标题、技术栈

Phase 4: URL 采集
  → katana（爬虫）→ gau（已知 URL）→ waybackurls（存档）
  → JS 文件提取（含隐藏端点）

Phase 5: 端口扫描
  → nmap 快速扫 top 1000 端口 → 识别服务版本

Phase 6: 目录/文件爆破
  → ffuf 目录扫描 → API 端点发现

Phase 7: 参数发现
  → arjun / x8 隐藏参数 → 参数挖掘

Phase 8: CI/CD 安全扫描（可选）
  → GitHub Actions 工作流分析 → 52 条规则
  → 检测表达式注入/密钥泄露/供应链攻击
```

### 3.2 外部工具矩阵（50+）

| 类别 | 工具 | 用途 |
|------|------|------|
| 子域名 | subfinder, amass, assetfinder | 被动枚举 |
| DNS | dnsx | 批量解析 |
| HTTP | httpx, katana | 存活探测+爬虫 |
| URL | gau, waybackurls | 历史 URL 收集 |
| 扫描 | nuclei, dalfox | 模板扫描+XSS |
| 爆破 | ffuf, kiterunner | 目录/API 爆破 |
| 密钥 | trufflehog, gitleaks | 密钥泄露检测 |
| 静态分析 | semgrep | 多语言安全审计 |
| 云 | cloud_enum | 公有云资产枚举 |

### 3.3 认证感知侦察（Auth-Aware Recon）

```bash
# 加载认证会话一次，所有下游工具自动携带
python3 tools/hunt.py --target T --cookie 'session=...'
python3 tools/hunt.py --target T --bearer 'eyJ...'
python3 tools/hunt.py --target T --auth-file .private/T.json

# IDOR/BOLA 双会话对比
python3 tools/hunt.py --target T --auth-file .private/T-user-a.json
python3 tools/hunt.py --target T --auth-file .private/T-user-b.json
```

认证令牌仅以 12 字符 hash 记录在日志中，原始值永不出现在日志/内存/hunt-memory。

---

## 四、自主渗透测试流程

### 4.1 5 阶段非线性工作流

```
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ 1. RECON │──▶│ 2. MAP   │──▶│ 3. FIND  │
    └────┬─────┘   └────┬─────┘   └────┬─────┘
         ▲               │              │
         │               ▼              ▼
         │         ┌──────────┐   ┌──────────┐
         └─────────│ 4. PROVE │◀──│ 5. REPORT│
                   └──────────┘   └──────────┘
```

- **Phase 0: 会话启动** — 定义目标（C/I/A/ATO/RCE），选择 1-2 种漏洞类型
- **Phase 1: 侦察** — 最大化攻击面，找到别人遗漏的资产
- **Phase 2: 映射分析** — 像开发者一样理解应用：端点地图+认证模型+业务流+JS分析
- **Phase 3: 漏洞发现** — 先基于错误，后基于盲测；按端点类型选择对应检测清单
- **Phase 4: 证明与升级** — 证明最大业务影响，将 Low 提升为 Critical
- **Phase 5: 报告** — 7 问门控 → 4 道提交关 → 专业报告

### 4.2 自主驾驶模式（Autopilot）

```bash
# 三种模式
/autopilot target.com --paranoid  # 保守模式：每次行动暂停确认
/autopilot target.com --normal    # 标准模式：关键节点暂停
/autopilot target.com --yolo      # 激进模式：完全自主（建议仅对已熟目标）
```

自主循环：**范围检查 → 侦察 → 攻击面排序 → 探测 → 验证 → 报告**，每阶段有安全检查点。

### 4.3 A→B 链式猎杀（信号法）

| 发现 A | 追猎 B | 升级到 C |
|---------|--------|-----------|
| IDOR（读） | 同端点 PUT/DELETE | 完整数据操控 |
| SSRF（任意） | 云元数据 169.254.169.254 | IAM 凭证外泄 → RCE |
| XSS（存储） | 检查 HttpOnly | 会话劫持 → ATO |
| 开放重定向 | OAuth redirect_uri | 授权码窃取 → ATO |
| S3 桶公开 | 枚举 JS bundles | grep OAuth client_secret |

### 4.4 验证门控体系

**7 问门控（写报告前必须全部通过）：**

| 问题 | 不通过 → 动作 |
|------|--------------|
| Q1: 攻击者现在能用的步骤模板？ | 写不出 HTTP 请求 → **杀死** |
| Q2: 影响在项目接受列表内？ | 映射到排除项 → **杀死** |
| Q3: 根因在范围内资产？ | 第三方/非生产 → **杀死** |
| Q4: 需要攻击者无法获得的特权？ | "Admin 能" → **杀死** |
| Q5: 已有已知/接受的行为？ | 公开报告/设计文档 → **杀死** |
| Q6: 能证明影响超过"技术可行"？ | 仅有理论 → **降级，不杀死** |
| Q7: 在永不提交列表里？ | 无链 → **杀死** |

**4 道提交关：**
- Gate 0: 现实检查（30 秒）— 确认真实可复现
- Gate 1: 影响验证（2 分钟）— 攻击者获得了什么
- Gate 2: 重复检查（5 分钟）— 搜索现有报告/issue
- Gate 3: 报告质量（10 分钟）— 标题公式+复制粘贴 PoC+CVSS 3.1

### 4.5 漏洞报告生成

**报告模板结构（影响优先）：**
- 标题公式：`[漏洞类型] 在 [端点] 允许 [攻击者] 达成 [影响]`
- 一句话影响声明
- 精确复现步骤（可复制粘贴的 HTTP 请求/响应）
- CVSS 3.1 向量 + 评分
- 建议修复方案
- 人类语气 → 禁用 "could potentially" / "may allow" 等 AI 废话

---

## 五、NΞXUS CC 代码安全审查集成方案

### 5.1 集成定位

```
NΞXUS 双引擎工作流：
  
  Hermes（编排层）                    Claude Code（执行层）
       │                                      │
       │  1. 发起编码任务                      │
       │──────────────────────────────────────▶│
       │                                      │ 2. 编写代码
       │                                      │ 3. 自检/自测
       │  4. 产出验收 ←───────────────────────│
       │                                      │
       │  ★ 新增：安全审查接口 ★               │
       │  5. 触发代码安全扫描                   │
       │     调用 claude-bug-bounty 工具链      │
       │     ├── 静态分析（semgrep）            │
       │     ├── 密钥泄露检测（trufflehog）      │
       │     ├── 依赖漏洞扫描（已知 CVE）        │
       │     ├── API 端点安全分析               │
       │     └── 代码逻辑漏洞模式匹配            │
       │                                      │
       │  6. 安全报告 ← 扫描结果                │
       │  7. 安全门控决策                        │
       │     ├── PASS → 代码合入                │
       │     ├── WARN → 标记风险，记录债务       │
       │     └── FAIL → 退回 CC 修复            │
```

### 5.2 具体实现方案

#### Phase 1: 安全扫描脚本化（Shell 层）

```bash
#!/bin/bash
# nexus-security-scan.sh — NΞXUS CC 代码安全审查脚本
# 在 CC 完成代码编写后，由 Hermes 自动触发

TARGET_DIR="${1:?Usage: $0 <code-directory>}"
REPORT_DIR="reports/security/$(date +%Y%m%d_%H%M%S)"

mkdir -p "$REPORT_DIR"

# 1. 静态安全分析（Semgrep — 多语言规则集）
echo "[*] Phase 1: 静态代码安全分析..."
semgrep --config=p/security-audit "$TARGET_DIR" \
  --json -o "$REPORT_DIR/semgrep.json" 2>/dev/null

# 提取高危结果
jq '.results[] | select(.extra.severity == "ERROR") | 
  {file: .path, rule: .check_id, line: .start.line, msg: .extra.message}' \
  "$REPORT_DIR/semgrep.json" > "$REPORT_DIR/semgrep-high.json"

# 2. 密钥泄露检测（Trufflehog）
echo "[*] Phase 2: 密钥泄露扫描..."
trufflehog filesystem "$TARGET_DIR" --json \
  > "$REPORT_DIR/trufflehog.json" 2>/dev/null

# 3. 依赖漏洞扫描
echo "[*] Phase 3: 依赖漏洞检查..."
# npm audit / pip-audit / cargo-audit 根据项目类型自动选择
if [ -f "$TARGET_DIR/package.json" ]; then
  cd "$TARGET_DIR" && npm audit --json > "$REPORT_DIR/npm-audit.json" 2>/dev/null
elif [ -f "$TARGET_DIR/requirements.txt" ]; then
  pip-audit -r "$TARGET_DIR/requirements.txt" --format json \
    > "$REPORT_DIR/pip-audit.json" 2>/dev/null
fi

# 4. 汇总报告
echo "[*] Phase 4: 生成安全报告..."
CRITICAL=$(jq '[.[] | select(.extra.severity=="ERROR")] | length' "$REPORT_DIR/semgrep-high.json" 2>/dev/null || echo 0)
SECRETS=$(jq 'length' "$REPORT_DIR/trufflehog.json" 2>/dev/null || echo 0)

echo "{\"summary\": {\"critical\": $CRITICAL, \"secrets\": $SECRETS, \"time\": \"$(date -Iseconds)\"}}" \
  > "$REPORT_DIR/summary.json"

# 5. 门控逻辑
if [ "$CRITICAL" -gt 0 ]; then
  echo "FAIL: $CRITICAL critical security issues found"
  exit 1
elif [ "$SECRETS" -gt 0 ]; then
  echo "WARN: $SECRETS potential secrets detected"
  exit 0
else
  echo "PASS: No critical issues"
  exit 0
fi
```

#### Phase 2: Hermes Skill 封装

在 Hermes 的 `skills/` 目录下创建 `cc-security-gate` skill：

```markdown
---
name: cc-security-gate
description: CC 代码安全门控 — CC 产出后自动触发漏洞扫描，作为验收的一环
---

# CC 代码安全门控

## 触发时机
CC 完成代码编写 → 提交产出 → Hermes 自动运行安全扫描

## 检查项
1. **静态分析** — semgrep p/security-audit 规则集
2. **密钥检测** — trufflehog 扫描硬编码凭证
3. **依赖漏洞** — npm-audit / pip-audit
4. **代码模式** — 已知漏洞模式匹配（SQLi / XSS / SSRF / IDOR / 路径遍历）

## 门控决策
| 结果 | 动作 |
|------|------|
| 0 critical + 0 secrets | ✅ PASS → 合入 |
| 0 critical + N secrets | ⚠️ WARN → 标记 + 记录技术债务 |
| ≥1 critical | ❌ FAIL → 退回 CC，附带具体文件+行号+修复建议 |

## 集成到 NΞXUS 流水线
CC 完成代码 → Hermes 运行 cc-security-gate → 产出验收报告
→ PASS 则进入下一阶段（测试生成 → 覆盖率验证）
```

#### Phase 3: 完整验收流水线

```
CC 代码产出
  │
  ├── 1. 安全门控（cc-security-gate）
  │      ├── PASS → 继续
  │      └── FAIL → 退回 CC + 具体原因
  │
  ├── 2. 测试生成（qodo-cover 集成）
  │      └── 覆盖率 ≥ 80%
  │
  ├── 3. 破坏性变更检测（code-review-graph）
  │      └── 爆炸半径分析
  │
  └── 4. 完整验收报告 → 合入决策
```

### 5.3 借用的关键机制

从 claude-bug-bounty 直接借用到 NΞXUS CC 安全审查：

| 机制 | 来源 | NΞXUS 用途 |
|------|------|------------|
| **7 问门控** | validator agent | 代码安全发现分类（Critical/Warn/Info） |
| **密钥检测管道** | /secrets-hunt | CC 产出中硬编码凭证扫描 |
| **CVE 情报** | /intel | 依赖库已知漏洞自动匹配 |
| **semgrep 多语言规则** | SKILL.md 静态分析节 | 代码注入模式检测 |
| **永不提交清单** | triage-validation | 低危发现自动过滤 |
| **条件有效+需要链** | conditionally-valid 表 | 组合漏洞标注 |
| **认证感知扫描** | auth-sessions | API 端点认证安全性检查 |

### 5.4 与现有 NΞXUS 工具链的配合

```
                             NΞXUS 验收流水线
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐        ┌──────────────────┐        ┌─────────────────┐
│ cc-security   │        │ qodo-cover       │        │ code-review     │
│ -gate         │        │ 测试生成          │        │ -graph          │
│               │        │                   │        │ 爆炸半径        │
│ 安全扫描       │   ──▶  │ 覆盖率验证         │   ──▶  │ 依赖影响        │
│ 密钥检测       │        │ 迭代补测          │        │ 死代码           │
│ 漏洞模式       │        │                   │        │                  │
└───────┬───────┘        └────────┬──────────┘        └────────┬─────────┘
        │                         │                            │
        ▼                         ▼                            ▼
  PASS/WARN/FAIL           覆盖率 ≥ 80%                 爆炸半径 ≤ 安全阈值
        │                         │                            │
        └─────────────────────────┼────────────────────────────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │ 合入决策      │
                          │ ALL PASS → ✅ │
                          │ ANY FAIL → ❌ │
                          └──────────────┘
```

---

## 六、关键洞察

### 6.1 对 NΞXUS 的价值

1. **安全左移**：CC 写完代码后立即扫描，而非等到上线后。Bug 在编码阶段解决成本最低。
2. **自动化验收**：安全门控成为 CC 产出验收的必要环节，减少人工审查负担。
3. **知识复用**：claude-bug-bounty 的猎杀记忆机制可借鉴——NΞXUS 可建立"代码安全模式库"，CC 产出安全缺陷自动归档→模式学习→下次编码时主动提醒。
4. **链式思维**：A→B 漏洞链概念可应用到代码审查——发现一个安全问题后，自动搜索关联的同类问题。

### 6.2 与现有方案对比

| 维度 | 传统方案 | claude-bug-bounty | NΞXUS 集成后 |
|------|----------|-------------------|-------------|
| 工具数量 | 10+ 手动切换 | AI 自动编排 | Hermes 统一编排 |
| 报告生成 | 45 分钟/份 | 60 秒/份 | 自动产出 |
| 跨会话记忆 | 无 | 猎杀记忆持久化 | 代码安全模式库 |
| 认证状态 | 每次手动加载 | 一次加载全局复用 | CC 产出自动关联 |
| 安全门控 | 人工判断 | 7 问门控 | 自动化安全门控 |

### 6.3 风险与限制

- **授权范围**：必须仅在授权测试范围内使用，误操作可导致法律风险
- **误报率高**：zero-day fuzzer 默认关闭（高误报），自动扫描结果需人工验证
- **速率限制**：过度自动化扫描可能触发 WAF/速率限制
- **环境依赖**：需要 50+ 外部工具安装，macOS/Linux 兼容性维护成本高

---

## 参考

- GitHub: https://github.com/shuvonsec/claude-bug-bounty
- 文档: https://github.com/shuvonsec/claude-bug-bounty#readme
- 作者: shuvonsec（https://shuvonsec.me）
- 版本: v4.3.0（2026-05）— 认证会话 + 侦察工具箱
