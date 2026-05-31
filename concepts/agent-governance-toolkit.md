---
id: 20260531-agent-governance-toolkit
title: Microsoft Agent Governance Toolkit 拆解 — 策略执行、零信任身份、沙箱隔离
tags: [hermes, agent-upgrade, security, governance, workflow, multi-agent]
source_url: https://github.com/microsoft/agent-governance-toolkit
date_created: 2026-05-31
last_updated: 2026-05-31
confidence: high
---

# Microsoft Agent Governance Toolkit（AGT）拆解

> ⭐ 3,481 | MIT License | Python/TS/.NET/Rust/Go 五语言 SDK | 992 项一致性测试 | 覆盖 OWASP Agentic Top 10 全部 11 类风险

## 🎯 WHAT — 核心问题与原理

### 它解决什么？

AI Agent 部署到生产环境后，面临三个致命问题：

1. **这个操作允许吗？** 拥有 `send_email` 和 `query_database` 权限的 Agent 不应该能 `drop_table`。OAuth scope 控制「能连什么服务」，但不控制「连上之后做什么」。
2. **哪个 Agent 干的？** 多 Agent 系统可能共享同一个 API Key。出事时"某个 Agent 干的"不是合格的事件响应。
3. **你能证明发生了什么吗？** 审计员和监管机构需要防篡改的决策记录：当时什么策略生效、Agent 请求了什么、为什么被允许或拒绝。

### AGT 的核心理念：确定性拦截，而非概率性请求

> Prompt 级别的安全（"请遵守规则"）不是控制面——那是对随机系统的礼貌请求。

AGT 不在 prompt 里打赢这场仗。每个工具调用、消息发送、Agent 委托都在**确定性应用代码**中被截获，**在模型意图到达执行层之前**就做出裁决。AGT 内核拒绝的操作不是"不太可能"，而是**结构性不可能**。

### 整体架构

```
Agent ──► Policy Engine ──► Identity ──► Audit Log
            (YAML/OPA/Cedar)  (SPIFFE/DID/mTLS)  (Tamper-evident)
                 │                                      │
                 ├── Allowed ──► Tool executes           │
                 └── Denied  ──► GovernanceDenied        │
                                                        ▼
                                                 Decision Record
```

### 8 大核心包

| 包 | 职责 |
|----|------|
| **Agent OS** | 策略引擎、Agent 生命周期、治理门禁 |
| **Agent Mesh** | Agent 发现、路由、信任网格 |
| **Agent Runtime** | 四环执行沙箱 |
| **Agent SRE** | Kill Switch、SLO 监控、混沌测试 |
| **Agent Compliance** | OWASP 验证、策略 lint、完整性检查 |
| **Agent Marketplace** | 插件治理与信任评分 |
| **Agent Lightning** | RL 训练治理与违规处罚 |
| **Agent Hypervisor** | 执行审计、Delta 引擎、承诺锚定 |

---

## 🛠️ HOW — 三大核心能力实现方式

### 1. 策略执行（Policy Enforcement）

**一句话：** 所有 Agent 操作流经一个拦截器链，YAML 声明策略 + 优先级排序 + 首匹配即停 + 失败即关闭。

#### 策略文档结构（PolicyDocument）

```yaml
apiVersion: governance.toolkit/v1
name: production-policy
default_action: allow
rules:
  - name: block-destructive
    condition: "action.type in ['drop', 'delete', 'truncate']"
    action: deny
    description: "破坏性操作需人工审批"

  - name: require-approval-for-send
    condition: "action.type == 'send_email'"
    action: require_approval
    approvers: ["security-team"]
```

#### 关键机制

**9 种条件运算符（RFC 2119 规范强制要求）：**

| 运算符 | 语义 | 示例 |
|--------|------|------|
| `eq` / `ne` | 等于 / 不等于 | `tool_name eq "execute_code"` |
| `gt` / `lt` / `gte` / `lte` | 数值比较 | `token_count gt 4096` |
| `in` | 成员判断 | `tool_name in ["read", "write"]` |
| `contains` | 包含检测 | `arguments contains "password"` |
| `matches` | 正则匹配 | `tool_name matches "^exec_.*"` |

**评估顺序（不可变）：**
1. 规则按 `priority` 降序排列（高优先先生效）
2. 首条匹配的条件决定结果，后续规则不再评估
3. 无 YAML 规则匹配 → 查询外部后端（OPA/Rego、Cedar）→ 无后端结果 → 使用 `defaults.action`
4. 任何评估异常 → 拒绝（Fail-Closed）

**目录层级策略合并：**
- 从操作路径向上遍历到根目录，加载沿途所有 `governance.yaml`
- 父 deny 规则不可被子覆盖（安全性不变量，类似 Azure Policy）
- `inherit: false` 可切断父级继承链
- 路径穿越攻击自动拒绝

**4 种冲突解决策略：**
| 策略 | 逻辑 |
|------|------|
| `DENY_OVERRIDES` | 任一 deny → 拒绝（XACML 语义，最安全） |
| `ALLOW_OVERRIDES` | 任一 allow → 允许（例外放行模式） |
| `PRIORITY_FIRST_MATCH` | 最高优先级胜出（默认） |
| `MOST_SPECIFIC_WINS` | Agent > Organization > Tenant > Global |

**工具调用拦截器链（短路拒绝）：**
```
1. Human Approval 检查
2. Allowed Tools 白名单
3. Blocked Patterns 黑名单（substring / regex / glob）
4. Call Count 上限（max_tool_calls）
→ 全通过 → ALLOW
```

---

### 2. 零信任身份（Zero-Trust Identity）

**一句话：** 每个 Agent 拥有 Ed25519 加密绑定的 DID + 持续计算的 0-1000 信任分 + 人肉 Sponsor 问责链。

#### Agent DID 体系

```
格式：did:mesh:<128位随机hex>
生成：secrets.token_hex(16) → 32 hex 字符（128 位熵）
```

每个 AgentIdentity 包含：
- `did` — 去中心化标识符
- `public_key` — Ed25519 公钥（base64）
- `sponsor_email` — **人肉担保者**（核心问责机制：「AI 无法被法律追责，Sponsor 绑定确保每个操作追溯到责任人」）
- `status` — `active` | `suspended` | `revoked`
- `capabilities` — 能力列表

**状态机：**
```
active → suspended（可 reactivate，但含 "security" 关键词则需 override）
active → revoked（不可逆，永不复活）
suspended → revoked
```

#### 信任分模型（0-1000）

**5 个加权维度：**
| 维度 | 权重 | 含义 |
|------|------|------|
| `policy_compliance` | 0.25 | 策略遵守度 |
| `resource_efficiency` | 0.15 | 资源使用效率 |
| `output_quality` | 0.20 | 输出质量 |
| `security_posture` | 0.25 | 安全行为 |
| `collaboration_health` | 0.15 | 协作健康度 |

**信任层级：**
| 层级 | 最低分 | 含义 |
|------|--------|------|
| `verified_partner` | 900 | 已验证合作伙伴 |
| `trusted` | 700 | 可信 Agent |
| `standard` | 500 | 新 Agent 默认值 |
| `probationary` | 300 | 观察期 |
| `untrusted` | 0 | 不可信（自动吊销凭证） |

**信任衰减与传播：**
- **时间衰减：** 无正面信号时每小时线性衰减 2.0 分（不低于 100）
- **信任传染：** Agent A 出问题时，与之交互过的 Agent 按 `影响 × 交互权重 × 传播因子 × 0.5^跳数` 连锁扣分
- **行为突变检测：** KL 散度检测近期 vs 基线行为分布，超过阈值 → `RegimeChangeAlert`

#### 凭证生命周期

- 短期 Bearer Token（默认 TTL 15 分钟）
- 仅存 SHA-256 哈希，原始 token 返回一次即丢弃
- 常量时间比较防时序攻击
- 轮换：旧凭证标记 `rotated` 而非 `revoked`（零停机重叠期）
- 能力匹配：精确 / 通配符 `*` / 前缀通配 `prefix:*`

#### IATP 握手协议（Inter-Agent Trust Protocol）

```
挑战者 → 发起 HandshakeChallenge（256位 nonce + 可选 RFC 9334 freshness nonce）
响应者 → 返回 HandshakeResponse（Ed25519 签名 + 自报信任分 + 能力列表）
挑战者 → 验证：challenge_id 匹配 + 未过期 + nonce 匹配 + 签名有效 + DID 匹配 + 信任分达标
→ 返回 HandshakeResult(verified, trust_level, capabilities)
```

DoS 防护：待处理挑战上限 1000，过期自动清理。

#### SPIFFE/SVID 集成

支持标准工作负载身份（`spiffe://trust_domain/agentmesh/...`），实现 Agent 间 mTLS。

---

### 3. 沙箱隔离（Execution Sandboxing）

**一句话：** 四环特权模型 + 信任分驱动环分配 + 时间限定的特权提升 + 基于 Token Bucket 的速率限制。

#### 四环执行模型（受 CPU 特权环启发）

| 环 | 值 | 名称 | 权限 | 分配条件 |
|----|----|------|------|----------|
| Ring 0 | 0 | Root | 系统配置、处罚操作 | **永不分配给 Agent**（需 SRE Witness 线下认证） |
| Ring 1 | 1 | Privileged | 不可逆操作、完整资源访问 | `eff_score > 0.95` **且** `has_consensus == true` |
| Ring 2 | 2 | Standard | 可逆操作、限定资源 | `eff_score > 0.60` |
| Ring 3 | 3 | Sandbox | 只读操作、最小资源 | 默认分配（未知/低信任 Agent） |

#### 每环资源约束

| 资源 | Ring 0 | Ring 1 | Ring 2 | Ring 3 |
|------|--------|--------|--------|--------|
| 网络 | ✅ 全部 | ✅ 全部 | ✅ 白名单 | ❌ 禁止 |
| 文件系统 | full | full | scoped | none |
| 子进程 | ✅ | ✅ | ✅ | ❌ |
| 最大并发工具 | 32 | 16 | 8 | 2 |

#### 操作分类 → 所需环

```
is_admin                          → Ring 0（系统独占）
reversibility == NONE && !read_only → Ring 1（不可逆操作）
is_read_only                      → Ring 3（只读）
其他                              → Ring 2（可逆操作）
```

#### 特权提升（Privilege Elevation）

- **时间限定：** 默认 300 秒，最长 1 小时，到期自动降级
- **信任门控：** Ring 1 需 trust_score ≥ 0.85，Ring 2 需 ≥ 0.50
- **Ring 0 禁止：** 标准 API 绝不允许提升到 Ring 0
- **子 Agent 继承：** 子 Agent 环级别 ≤ 父 Agent 有效环

#### 速率限制（Token Bucket）

| 环 | 速率 (req/s) | 突发 |
|----|--------------|------|
| Ring 0 | 100.0 | 200.0 |
| Ring 1 | 50.0 | 100.0 |
| Ring 2 | 20.0 | 40.0 |
| Ring 3 | 5.0 | 10.0 |

环变更时重建 Token Bucket，最大活跃桶数 100,000。

#### Kill Switch

- 支持 6 种终止原因：`behavioral_drift` / `rate_limit` / `ring_breach` / `manual` / `quarantine_timeout` / `session_timeout`
- 优先尝试步骤移交（Step Handoff）给注册的替补 Agent
- 回调超时默认 5 秒，失败不阻止终止记录

#### 审计哈希链

每个操作记录为 SemanticDelta，包含 `previous_hash` → `delta_hash`（SHA-256）。任何篡改将破坏后续所有哈希——实现**可检测不可否认**的审计轨迹。

#### 会话隔离

| 级别 | 描述 | 代价 |
|------|------|------|
| `SNAPSHOT` | 完全隔离，仅见自身会话 | 低 |
| `READ_COMMITTED` | 可读已授权会话，写仅自身 | 中 |
| `SERIALIZABLE` | 完整因果排序 + 向量时钟 + 意图锁 | 高 |

---

## 🔄 APPLICATION — 与 NΞXUS 双引擎防作弊的对接方案

> 参考：[[nexus-dual-engine]] — 当前 NΞXUS 防作弊是「人工规则 + Agent 自律」，AGT 提供了**确定性拦截层**来替代信任。

### 对接点一：用 Policy Engine 替代「防作弊规则表」

当前 NΞXUS 防作弊规则（虚构文件内容、声称测试通过但没跑、跳过验收等）是**文档声明**，靠 Agent 自觉遵守。用 AGT Policy Engine 可将这些规则变为**代码级强制执行**：

```yaml
# nexus-policy.yaml
apiVersion: governance.toolkit/v1
name: nexus-anti-cheat
default_action: allow
rules:
  - name: no-fabricated-output
    condition: "action.metadata.has_evidence ne true"
    action: deny
    priority: 100
    message: "所有 CC 产出必须有物证（文件路径/测试输出）"

  - name: block-unverified-claim
    condition: "action.type == 'task_report' and action.evidence.verification_passed ne true"
    action: deny
    priority: 90
    message: "报告声称完成但验证未通过"

  - name: require-git-trace
    condition: "action.type in ['code_change', 'bug_fix'] and action.metadata.commit_hash eq null"
    action: deny
    priority: 80
    message: "代码变更必须有 Git commit 溯源"

  - name: block-truncated-task
    condition: "action.type == 'task_dispatch' and action.metadata.five_questions_complete ne true"
    action: deny
    priority: 110
    message: "任务分发前必须完成 5 问需求确认"
```

### 对接点二：用 Identity + Trust Score 区分 Hermes 和 CC

```
Hermes DID: did:mesh:hermes-orchestrator（trust_score >= 900, verified_partner）
CC DID:    did:mesh:claude-code-worker（trust_score 动态计算）
```

- Hermes 作为编排器获得高信任分 → Ring 2（Standard）权限
- CC 作为代码执行者，信任分由**实际产出验证结果**驱动：
  - 物证齐全 + 测试通过 → `policy_compliance` +10
  - 声称完成但无证据 → `security_posture` -30 + 记录违规
  - 连续 3 次无验证 → 自动降级到 Ring 3（只读），禁止写代码

### 对接点三：用 Audit Hash Chain 做不可篡改的「飞轮日志」

当前飞轮日志是 Markdown 表格，可手动修改。用 AGT 审计哈希链：

```
每一轮任务完成 → SemanticDelta {
    agent_did: "did:mesh:claude-code-worker",
    action: "task_completed",
    previous_hash: "<上一条哈希>",
    delta_hash: "SHA-256(本轮所有操作)"
}
```

任何对历史日志的修改都会破坏哈希链，实现**可验证的防篡改**。

### 对接点四：Hermes 作为 AGT PolicyEvaluator 的调用者

```python
from agent_os.policies import PolicyEvaluator
from agent_os.governance import govern

# Hermes 包装 CC 的所有工具调用
@govern(policy="nexus-policy.yaml")
def cc_write_code(file_path, content):
    # CC 的实际写代码操作
    pass

@govern(policy="nexus-policy.yaml")
def cc_run_tests(test_suite):
    # CC 的实际测试执行
    pass

@govern(policy="nexus-policy.yaml")
def cc_git_commit(message, files):
    # CC 的实际 Git 操作
    pass
```

### 对接优先级建议

| 阶段 | 对接内容 | 预期收益 |
|------|----------|----------|
| **Phase 1（本周）** | Policy Engine 替代防作弊规则表 | 从文档声明 → 代码强制 |
| **Phase 2（下周）** | 审计哈希链接入飞轮日志 | 从可篡改 Markdown → 不可否认 |
| **Phase 3** | Trust Score 驱动 CC 权限动态调整 | 低信任自动限权 |
| **Phase 4** | IATP 握手替代当前 `start-claude` 脚本 | 加密认证替代进程启动 |

---

## 📊 飞轮日志

| 轮次 | 日期 | 操作 |
|------|------|------|
| 初始 | 2026-05-31 | 完成 AGT 拆解 Wiki：抓取 README + 3 份 RFC 规范 + OWASP 架构文档，输出策略执行/零信任身份/沙箱隔离三大核心能力分析及 NΞXUS 对接方案 |
| 待定 | — | Phase 1：部署 `govern()` 包装 CC 工具调用 |
| 待定 | — | Phase 2：接入审计哈希链 |
