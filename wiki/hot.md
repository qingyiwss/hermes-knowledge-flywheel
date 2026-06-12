# Hot Cache — 最新上下文
> 更新: 2026-06-12 · Wiki: 54篇 · P1: Token优化已修复(双引擎) | SOUL.md已激活

## 最近事件
- 🛠️ 网关重启后优化参数丢失（threshold_pct→10, child_timeout→600），已全部恢复
- 🆕 SOUL.md 写入并激活，personality 生效
- 📝 growth-log + lessons-learned 追加，飞轮库保持同步
- 🧠 用户要求：token 优化 + 执行效率 → 已完成配置修复
- 📌 **新规则：飞轮必须同时同步 Obsidian 知识库**（growth-log.md + lessons-learned.md + wiki/hot.md → git push）

## 生效中的优化（下次飞轮即生效）
- threshold_pct: 3（10→3，省~2,300 tokens/轮）
- child_timeout: 300（600→300，省~50% 子Agent空转）
- max_iterations: 15（20→15，限制子Agent循环层次）
- personality: SOUL.md（效率导向 persona，省~150 tokens/轮）
