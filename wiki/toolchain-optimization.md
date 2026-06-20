# 工具链优化 — NΞXUS 效率提升
> 创建: 2026-06-20 · 迭代: 第3轮 · 作者: Hermes (mimo-v2.5-pro)

## 工具调用优化

### 1. 并行工具调用
- **规则**：无依赖的工具调用必须在同一轮并行发出
- **案例**：搜索 + 读文件 + 检查状态 → 一轮完成
- **收益**：减少轮次 → 减少上下文膨胀 → 省 Token

### 2. 工具选择优化
| 场景 | 推荐工具 | 替代方案 | 为什么 |
|------|---------|---------|--------|
| 读文件 | read_file | terminal cat | 更快，有行号 |
| 搜索文件 | search_files | terminal grep | 更快，支持正则 |
| 编辑文件 | patch | terminal sed | 更安全，有验证 |
| 创建文件 | write_file | terminal echo | 更快，自动创建目录 |
| 网页搜索 | web_search | browser | 更快，更省 |
| 网页提取 | web_extract | browser | 更快，更省 |
| 代码任务 | delegate_task CC | 自己写 | 角色分离 |
| 监控任务 | cron no_agent | cron agent | 零消耗 |

### 3. 避免不必要的工具调用
- **反模式**：先 ls 看目录 → 再 cat 看文件 → 再编辑（3 次调用）
- **优化**：直接 read_file 读取 → patch 编辑（2 次调用）
- **收益**：减少 33% 工具调用

## 子代理（CC）优化

### 任务描述精确度
| 描述质量 | 执行结果 | Token 消耗 |
|---------|---------|:---:|
| "优化一下" | 猜测 → 重做 2-3 轮 | 高 |
| "优化 auth.ts 第 45-60 行的 JWT 验证逻辑" | 一步到位 | 低 |
| "修复 bug" | 需要调试 → 多轮 | 高 |
| "修复 LoginModal.tsx 的空指针：email 为空时 line 23 报错" | 直接修复 | 低 |

### 超时控制
- **默认**：300 秒（5 分钟）
- **简单任务**：120 秒（2 分钟）
- **复杂任务**：600 秒（10 分钟）
- **规则**：超时后不重试，改为更精确的任务描述重发

### 循环验证
```bash
# hermes-cc-loop.sh 用法
bash hermes-cc-loop.sh -d /path/to/project -t "fix login bug" -c "npm test" -m 3
# -c: 验证命令（测试/构建/lint）
# -m: 最大迭代次数
# 自动重试直到验证通过或达到上限
```

## LCM 压缩优化

### 压缩时机
- **默认**：60% 上下文窗口时压缩
- **MiMo 优化**：20%（200K）时压缩（1M 窗口的 20%）
- **理由**：早压缩 → 保持更多有效上下文 → 减少幻觉

### 压缩模式
| 模式 | Token 保留 | 适用场景 |
|------|:---:|------|
| BALANCED | 8-10% | 默认，平衡精度和压缩 |
| AGGRESSIVE | 4-6% | 长会话，需要更多空间 |
| PRECISION | 12-15% | 关键任务，不丢细节 |

### CACHE_FRIENDLY_CONDENSATION
- **开启**：压缩后的内容格式化为前缀友好
- **效果**：提升压缩后内容的缓存命中率
- **建议**：始终开启

## 文件操作优化

### 批量编辑
- **反模式**：逐个 patch 调用（N 次调用）
- **优化**：使用 patch mode='patch' 批量编辑（1 次调用）
- **收益**：减少 N-1 次工具调用

### 搜索优化
- **精确搜索**：search_files pattern="specific_function_name"
- **避免**：terminal grep（更慢，无正则支持）
- **技巧**：用 file_glob 限定文件类型（如 "*.py"）

## 网络请求优化

### web_search vs browser
| 维度 | web_search | browser |
|------|:---:|:---:|
| 速度 | 快（<5s） | 慢（>10s） |
| Token 消耗 | 低 | 高 |
| 适用 | 信息搜索 | 交互操作 |
| 动态内容 | 不支持 | 支持 |

### web_extract vs browser
| 维度 | web_extract | browser |
|------|:---:|:---:|
| 速度 | 快（<10s） | 慢（>15s） |
| Token 消耗 | 低 | 高 |
| 适用 | 静态页面 | 动态页面 |
| 内容提取 | 自动摘要 | 需手动提取 |

## Cron 任务优化

### no_agent 模式
- **适用**：数据采集、参数巡检、价格追踪、定时报告
- **收益**：零 Token 消耗，<5 秒延迟
- **限制**：需要推理/判断的任务仍需智能体模式

### 脚本优化
```bash
# 好的脚本：简洁输出，仅在异常时报告
#!/bin/bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://api.example.com/health)
if [ "$STATUS" != "200" ]; then
  echo "⚠️ API 健康检查失败: HTTP $STATUS"
fi
# 正常时无输出 → 静默

# 坏的脚本：每次都有输出
#!/bin/bash
echo "开始检查..."
curl https://api.example.com/health
echo "检查完成"
# 每次都发消息 → 烦人
```

## 参考

- Anthropic: Claude 最佳实践 (2026-06)
- NΞXUS 内部经验：CC 任务描述优化
- MiMo 官方文档：API 参数优化
