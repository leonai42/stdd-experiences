---
experience_id: EXP-PY-0002
category: scope_creep
pattern: "AI 在实现过程中主动 '优化' 或 '重构' 了计划范围外的代码，引入非预期的变更"
root_cause: |
  AI 模型在理解一段代码时，会自然识别出代码中 "不够好" 的部分（命名不规范、缺少类型注解、
  函数过长、重复代码等），并倾向于 "顺手修复"。这种倾向在对话式编程中通常是好习惯，
  但在规范驱动的开发流程中，任何超出 proposal 范围的改动都增加了回归风险。
  
  此外，AI 对 "小改动" 的定义与人类不同——AI 认为 "只是加了个类型注解" 可能
  实际上修改了函数签名，导致下游调用方需要同步适配。
detection_trigger: |
  - git diff --stat 显示的变更文件数超过 proposal 声明的 Impact 范围
  - 变更中出现了 proposal 未提及的模块/文件
  - Code Review 中发现 "顺手优化" 类型的改动
fix_template: |
  1. 在 Phase 4 BUILD 开始前，AI 必须输出 "本次切片即将修改的文件清单" 并等待确认
  2. 如果 AI 在编码过程中发现计划外需要修改的点：
     - 记录到 pending-adjustments（而非直接动手改）
     - 标注严重程度和是否阻塞当前切片
     - 等待用户决定：现在修 / 记入技术债 / 忽略
  3. Phase 5 VERIFY 中运行 git diff --stat 对比 proposal 的 Impact 声明
language: python
tags:
  - scope-control
  - refactoring
  - discipline
  - code-review
severity: medium
confidence: 0.78
occurrences: 2
frameworks:
  - any
first_seen: "2026-05-10"
last_seen: "2026-05-21"
provenance: ai-inferred
provenance_weight: 0.60
---

## 详细描述

在一个 API 限流功能的开发中，proposal 声明的变更范围是：
- 新增 `middleware/rate_limit.py`
- 修改 `app/core/config.py`（新增 RateLimitConfig）

但 AI 在实现过程中发现 `app/core/config.py` 中的 `DatabaseSettings` 类 "可以使用 pydantic v2 的新语法"（`model_config = ConfigDict(...)` 替代 `class Config:`），顺手做了修改。这个改动：
1. 不在 proposal 范围内
2. 影响了其他使用 `DatabaseSettings` 的模块（3 个文件需要同步适配）
3. 绕过了 Gate 2 的设计审核

## 根因链

1. **直接原因**：AI 主动 "优化" 了计划范围外的代码
2. **AI 为什么这样做**：AI 被训练为 "写出好代码"，遇到可以改进的地方自然会想改。范围意识（scope awareness）是后天训练的结果，不是默认行为
3. **为什么流程没有阻止**：Phase 4 开始前没有显式确认 "即将修改的文件清单"，AI 有自由裁量空间

## 代码示例

### ❌ 范围蔓延的例子
```python
# proposal 只要求加 RateLimitConfig
# 但 AI 还顺手把已有的 DatabaseSettings 也改了：

# app/core/config.py (AI 的范围外修改)
class DatabaseSettings:
    model_config = ConfigDict(env_prefix="DB_")  # AI 顺手升级语法
    
    url: str
    pool_size: int = 10
```

### ✅ 正确的做法
```python
# 只做 proposal 要求的改动，格式保持与现有代码一致
class RateLimitConfig(BaseSettings):
    max_requests: int = 100
    window_seconds: int = 60
    whitelist_ips: list[str] = []
    
    class Config:          # 保持与项目现有风格一致
        env_prefix = "RATE_LIMIT_"
```

## 对应失败模式

**(b) 范围蔓延（scope_creep）**：实现超出了 proposal 声明的变更范围，引入未审核的修改。

## 改进方向

- **短期**：Phase 4 BUILD Step 0 增加 "声明即将修改的文件清单" 步骤
- **长期**：STDD Phase 5 VERIFY 增加 `stdd ci check-scope` 自动检测范围蔓延
- **团队规范**：Code Review 中明确区分 "计划内改动" 和 "顺手优化"，后者需要额外审核
