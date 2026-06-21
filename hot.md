# 🔥 Hot — 最新上下文

> 最后更新：2026-06-20 | 模型：MiMo-V2.5-Pro

---

## 当前状态

- **Hermes 配置**：mimo-v2.5-pro（xiaomi 提供商）
- **CC 配置**：mimo-v2.5-pro（主模型）+ mimo-v2-flash（子代理）
- **飞轮库**：6 个（hermes/quant/trade/game/video/novel）
- **Wiki 总数**：64 篇
- **最近飞轮**：工作方式升级（多轮提问 + 对结果负责）

## 最新 Wiki（2026-06-20）

1. `hermes-workstyle-upgrade.md` — Hermes 工作方式升级
2. `claude-code-best-practices.md` — CC 最佳实践
3. `mimo-v25pro-optimization.md` — MiMo 模型优化
4. `cost-monitoring.md` — 成本监控
5. `toolchain-optimization.md` — 工具链优化
6. `verification-strategy.md` — 实战验证框架
7. `best-practices-summary.md` — 最佳实践速查表

## 已实施的优化

1. ✅ 辅助模型分层（mimo-v2-flash 省 75%）
2. ✅ LCM 早压缩（20% 阈值）
3. ✅ 工具搜索优化（3% 阈值）
4. ✅ 子代理超时（300 秒）
5. ✅ no_agent Cron（零消耗）
6. ✅ 并行工具调用（已生效）
7. ✅ 专用工具优先（已生效）

## 核心规则

- **多轮提问**：每轮 2-3 个问题，根据回答深入
- **对结果负责**：执行前确认 → 执行中验证 → 执行后跟踪
- **语言习惯**：极简直令 = 隐含需求，不追问不催办
- **触发词**："魏松山" = 读飞轮修正，"飞轮" = 沉淀知识

## 预期收益

| 场景 | 优化前 | 优化后 | 节省 |
|------|:---:|:---:|:---:|
| 普通对话 | 5000 Token | 2500 Token | 50% |
| 代码任务 | 15000 Token | 8000 Token | 47% |
| 网页研究 | 10000 Token | 5000 Token | 50% |
| 监控任务 | 500 Token | 0 Token | 100% |
| **日均费用** | **¥15-20** | **¥5-8** | **60-67%** |
