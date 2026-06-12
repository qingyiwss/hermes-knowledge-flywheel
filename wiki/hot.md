# Hot Cache — 最新上下文
> 更新: 2026-06-12 · Wiki: 54篇 · P1: Token优化已修复(双引擎) | SOUL.md已激活 | 底层规则落地

## 最近事件
- 🛠️ 网关重启后优化参数丢失（threshold_pct→10, child_timeout→600），已全部恢复
- 🆕 SOUL.md 写入并激活，personality 生效，新增3条底层规则
- 🆕 底层规则落地：结论格式(魏松山大人+方案总结+消耗预估)、丢规则触发词(魏松山)、结束语铁律(## ✅ 小结+Token消耗)
- 📝 growth-log + lessons-learned 追加，飞轮库保持同步

## 生效中的优化
- threshold_pct: 3
- child_timeout: 300
- max_iterations: 15
- personality: SOUL.md（含「魏松山」方案确认制 + 恢复机制）

## 底层规则
- 结论开头: "魏松山大人" + 方案总结 + 预估 token/费用
- 输入"魏松山"→ 丢规则，读飞轮库修正自己
- 多步骤任务 → ## ✅ 小结 + Token消耗行
- 飞轮后 → git commit + push 知识库三件套
