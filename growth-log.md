# 进化日志

> 知识飞轮的成长轨迹。每次拆解一个项目后追加。

## [2026-05-29] TradingAgents 多智能体交易架构

- **来源：** https://github.com/TauricResearch/TradingAgents
- **学到了什么：**
  1. **辩论机制**：Bull/Bear 对立研究员 + Aggressive/Neutral/Conservative 三方风控辩论，用对抗性讨论降低单模型偏见
  2. **双 LLM 策略**：廉价模型做数据扫描（分析师），昂贵模型做最终决策（经理），token 经济学
  3. **交易记忆闭环**：pending → 结果 → 反射 → resolved，历史教训自动注入未来 Prompt
  4. **结构化输出**：五档评级（Buy/Overweight/Hold/Underweight/Sell），确定性正则解析，不额外调 LLM
- **能力提升：**
  - Reasonix 可以从单路径分析升级为辩论式分析
  - 可以增加交易记忆模块，让回测结果反哺策略优化
  - 双模型策略可直接套用（flash + pro）
- **下一步：**
  - 在 Reasonix 回测中实现 bull/bear 双参数并行
  - 探索 LangGraph 替代当前线性脚本的可能性
