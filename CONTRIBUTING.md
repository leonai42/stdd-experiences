# 贡献指南 / Contributing Guide

感谢你考虑向 STDD 社区经验池贡献经验！

---

## 目录

1. [如何贡献一条经验](#如何贡献一条经验)
2. [经验质量标准](#经验质量标准)
3. [脱敏检查清单](#脱敏检查清单)
4. [经验条目文件格式](#经验条目文件格式)
5. [PR 审核流程](#pr-审核流程)

---

## 如何贡献一条经验

### 第 1 步：确认经验是否值得贡献

一条好的社区经验应该满足以下条件：

- ✅ **可复现**：同一个错误模式在你的项目中出现了 ≥2 次
- ✅ **通用性**：不依赖特定业务逻辑或项目结构
- ✅ **可操作**：有明确的检测触发条件和修复模板
- ✅ **分类正确**：匹配 STDD 的 11 类失败模式之一

### 第 2 步：使用模板撰写

复制 `community/.experience-template.md`，按照模板填写所有必填字段。

### 第 3 步：脱敏处理

运行脱敏检查（见[脱敏检查清单](#脱敏检查清单)），确保不包含敏感信息。

### 第 4 步：提交 PR

1. Fork 本仓库
2. 将你的经验文件放入 `community/proposals/` 目录
3. 文件名格式：`<language>-<short-slug>.md`，如 `python-async-cancelled-error.md`
4. 提交 PR，标题格式：`[Proposal] <语言>: <一句话摘要>`

### 第 5 步：社区审核

PR 提交后，社区维护者会进行审核。审核标准见[PR 审核流程](#pr-审核流程)。

---

## 经验质量标准

### 必填字段（缺少任一将被退回）

| 字段 | 要求 |
|------|------|
| `pattern` | 一句话描述错误模式，清晰、准确 |
| `category` | 匹配 11 类失败模式之一 |
| `root_cause` | 说明为什么 AI 会犯这个错（非表面原因） |
| `fix_template` | 可操作的修复方案（代码模板或步骤清单） |
| `language` | 主要编程语言 |
| `tags` | 至少 2 个标签，便于搜索匹配 |

### 质量加分项

- ✅ 包含**根因链**（root cause chain）：从现象到本质的多层分析
- ✅ 包含**检测触发器**（detection_trigger）：什么信号可以自动发现这个模式？
- ✅ 包含**置信度说明**（confidence rationale）：为什么给这个置信度分数？
- ✅ 包含**反例**（counter-example）：什么情况下这个经验**不适用**？
- ✅ 多语言适用（在 `tags` 中标注其他受影响的框架/库）

---

## 脱敏检查清单

提交前逐项确认：

### 路径与文件名
- [ ] 所有绝对路径替换为 `<project>/<module>/<file>` 格式
- [ ] 包名/模块名保留（如 `aiohttp`、`django` 是公共库，无需脱敏）

### 网络与基础设施
- [ ] IP 地址替换为 `<ip>` 或示例 IP（如 `192.0.2.1`）
- [ ] 域名替换为 `<domain>` 或 `example.com`
- [ ] API 端点路径脱敏：`/api/v1/users/<id>` → `/api/<version>/<resource>/<id>`

### 密钥与凭证
- [ ] 无 API Key / Token / Password / Secret
- [ ] 无数据库连接字符串
- [ ] 无证书内容

### 业务信息
- [ ] 公司/产品名称替换为 `<company>` / `<product>`
- [ ] 业务专有名词替换为 `<entity>`
- [ ] 用户数据（姓名/邮箱/手机号）替换为占位符

### 保留内容（无需脱敏）
- ✅ 编程语言和版本号
- ✅ 框架/库名称和版本号
- ✅ 异常类型（如 `asyncio.CancelledError`）
- ✅ 设计模式名称（如 `Singleton`、`Factory`）
- ✅ 代码片段（已脱敏路径和变量名后）

---

## 经验条目文件格式

每条经验是一个独立的 Markdown 文件，包含 YAML frontmatter + Markdown body：

```markdown
---
experience_id: EXP-PY-NNNN      # 提交时留空，由维护者分配
category: cascading_errors       # STDD 11 类失败模式之一
pattern: "一句话描述"
root_cause: "根因分析"
detection_trigger: "检测信号"
fix_template: "修复方案"
language: python
tags:
  - async
  - error-handling
severity: high                   # critical / high / medium / low
confidence: 0.85                 # 0.0-1.0，附说明
occurrences: 2                   # 在本项目中出现的次数
---

## 详细描述

...（Markdown 格式，可包含代码块）

## 根因链

...（从现象到本质的分析）

## 对应失败模式

...（映射到 STDD 11 类失败模式）

## 改进方向

...（长期/短期改进建议）
```

---

## PR 审核流程

```
PR 提交
  │
  ├── 自动化检查（GitHub Actions）
  │   ├─ YAML frontmatter 必填字段完整性
  │   ├─ 脱敏规则检查（无 IP/域名/密钥）
  │   └─ 文件命名规范
  │
  ├── 人工审核（社区维护者）
  │   ├─ 模式是否可复现？
  │   ├─ 根因分析是否到位？
  │   ├─ 修复方案是否可操作？
  │   └─ 脱敏是否彻底？
  │
  ├── 审核结果
  │   ├─ ✅ 通过 → 分配 experience_id，合并到对应语言包
  │   ├─ 📝 需修改 → 标注修改意见，作者更新后重新审核
  │   └─ ❌ 拒绝 → 标注原因（不通用/不可复现/已有类似经验）
  │
  └── 合并后
      ├─ 更新 experience-pack.yaml（版本号 + 条目数）
      ├─ 创建新的 GitHub Release
      └─ 用户可通过 stdd experience pull 拉取
```

---

## 11 类失败模式速查表

| ID | 类别 | 中文名 | 典型场景 |
|----|------|--------|---------|
| (a) | hallucination | 幻觉行为 | AI 使用了不存在的 API / 库 |
| (b) | scope_creep | 范围蔓延 | 改动超出 proposal 声明的范围 |
| (c) | cascading_errors | 级联错误 | 一个模块的错误波及下游模块 |
| (d) | context_loss | 上下文丢失 | 长对话中 AI 忘记早期决策 |
| (e) | tool_misuse | 工具误用 | AI 用错了 CLI 工具或命令参数 |
| (f) | runtime_deviation | 运行时偏离 | 运行时行为与 spec 不一致 |
| (g) | pipeline_break | 管线断链 | 文件引用/链接断裂 |
| (h) | content_quality | 内容质量偏差 | 生成内容格式/风格不一致 |
| (i) | instruction_decay | 指令衰减 | 长期规则被近期行为覆盖 |
| (j) | coverage_vacuum | 覆盖真空 | 有 spec 但无测试覆盖 |
| (k) | contract_gap | 契约断层 | API 接口前后端不一致 |
