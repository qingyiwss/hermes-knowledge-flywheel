---
id: 20260529-robotframework
title: Robot Framework — 验收测试驱动的需求验证
tags: [skill-learning, testing, bdd, atdd, qa, ci-cd]
source_url: https://github.com/robotframework/robotframework
date_created: 2026-05-29
last_updated: 2026-05-29
---

## 🎯 核心痛点与应用场景

**痛点：** 需求文档写完就过时，测试用例和需求描述是两套语言。需求说"用户可登录"，测试写 `test_login_returns_200()`——两者之间没有机器可读的追溯。

**Robot Framework 方案：** 用自然语言（关键字驱动）写测试，非技术人员也能读。需求文档本身就是可执行的测试。一条需求 = 一个可运行的验收测试。

```
需求：用户可以登录
  ↓ 直接转化为
Test Case: Valid Login
    Open Browser  ${URL}  Chrome
    Input Text  username  admin
    Input Text  password  ****
    Click Button  Login
    Page Should Contain  Welcome
```

## 🛠️ 底层原理解析

**架构三层：**
```
Test Data（测试数据层）
  ├─ 用自然语言关键字写测试用例
  ├─ 支持变量、数据表、模板
  └─ .robot 文件格式

Robot Framework Core（核心引擎）
  ├─ 解析 .robot → 执行关键字 → 生成报告
  ├─ 支持 Tag 分组、Setup/Teardown
  └─ 并行执行（pabot）

Test Libraries（测试库层）
  ├─ BuiltIn: 内置关键字（Should Be Equal, Log...）
  ├─ SeleniumLibrary: Web UI 测试
  ├─ RequestsLibrary: API 测试
  ├─ DatabaseLibrary: 数据库测试
  └─ 自定义 Python/Java 库
```

**关键字驱动（Keyword-Driven）的本质：**
```
高级关键字（业务语言）: "用户登录成功"
  ↓ 由以下组成
中级关键字（操作语言）: "输入用户名" → "输入密码" → "点击登录"
  ↓ 调用
低级关键字（技术实现）: SeleniumLibrary.Input Text
```

**CI 集成：**
```bash
# 运行所有标记为 smoke 的测试（冒烟测试=核心需求验证）
robot --include smoke tests/
# 输出: report.html（需求覆盖报告）+ log.html（执行日志）
```

## 🔄 Hermes 进化映射 (Integration Roadmap)

**对监控/testing 体系的影响：**
- cc 写代码后 → 自动跑 `.robot` 验收测试 → 需求是否回归一目了然
- 面板可集成 Robot Framework 报告 → 显示"需求覆盖率"指标

**具体落地步骤：**
1. 为核心功能编写 `.robot` 验收测试（登录、面板刷新、状态更新）
2. 在 `hermes-cc.sh` 完成后加一步：`robot tests/` 验证
3. 面板新增"需求覆盖率"卡片 → 从 `report.html` 解析

**门槛极低：** `pip install robotframework && robot --version` 即可，0 系统依赖。

**相关笔记：** [[doorstop-requirements-management]]、[[nexus-monitor-design]]、[[ci-cd-pipeline-patterns]]
