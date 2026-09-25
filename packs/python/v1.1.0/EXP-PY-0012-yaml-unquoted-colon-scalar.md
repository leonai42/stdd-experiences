---
experience_id: EXP-PY-0012
category: content_quality
pattern: "YAML 标量值含冒号（如英文 Key: Value 形态，或中文括号里出现的英文冒号）却未加引号，生成的文档解析报 ScannerError / ParserError"
root_cause: |
  写规格 YAML 时把含「: 」的文本裸放在未加引号的标量里；同一次改动内连续踩中 3 处
  （两处证据字段、一处偏离原因字段）。

  这些字段的内容天然是「句子 / 结论」形态（证据描述、偏离原因），中文写作里冒号极常见，
  而生成时注意力在「内容对不对」，不在「这个值需不需要引号」。YAML 的词法规则把
  「: 」视为映射分隔符，因此括号不构成保护 —— 括号内的英文冒号一样会让标量中途
  变成映射起始。
detection_trigger: |
  - yaml.safe_load 报 "mapping values are not allowed here" 或 "cannot start any token"
  - 正在写入含英文冒号加空格的值（类似 Key: Value 的形态）
  - 更早的信号：写入路径上没有任何解析步骤，错误推迟到渲染 / 机检阶段才爆发
fix_template: |
  1. 含冒号的 YAML 值一律整体加单引号
  2. 写入后立即用 yaml.safe_load 回读验证，不等渲染 / 机检时报错
language: python
tags:
  - yaml
  - quoting
  - ci
  - serialization
severity: medium
confidence: 0.85
occurrences: 1
audit_source: EXP-c7585f40940b
---

## 详细描述

在写规格 YAML 时，把含「冒号 + 空格」的文本直接裸放进未加引号的标量里。YAML 的词法规则把 `: ` 当作映射的键值分隔符，于是解析器在一个标量中途遇到了「映射起始」，直接抛出 `ScannerError` / `ParserError`（常见报错为 `mapping values are not allowed here` 或 `cannot start any token`）。

值得注意的是括号不构成保护：中文括号里写一个英文冒号，同样会触发 —— 解析器看的是字符本身，不是它被包在什么标点里。

本次是**同一次改动内连续踩中 3 处**（两处证据字段、一处偏离原因字段），说明它不是偶发笔误，而是同一类内容的批量重复：这些字段的取值天然是句子形态，而中文技术写作里冒号极其常见。

时间差也是这个模式的一部分：YAML 是拼装出来的文本，写入路径上**没有解析步骤**，所以错误不在产生它的那一刻暴露，而推迟到渲染或机检读取时才爆发 —— 此时已经跨了多个文件、多次提交，定位成本被放大。

## 根因链

1. **现象层**：生成出来的 YAML 无法解析，报 `ScannerError` / `ParserError`，整个文档读不进来。
2. **直接原因**：含 `: ` 的值没有加引号，YAML 把冒号之后的部分当成新的映射起始。
3. **为什么一次踩中 3 处**：这些字段的内容是「句子 / 结论」（证据描述、偏离原因），冒号是自然写法；生成时的注意力集中在**内容正确性**上，而引号需求属于**文本表示层**的约束 —— 前者是显式的写作目标，后者只在解析失败时才会被想起。
4. **为什么没在写入时发现**：写入路径只做字符串拼接，没有解析校验。YAML 的完整性检查被放在了下游（渲染 / 机检），于是错误与它的成因之间隔了多个文件和多次提交，回溯成本被显著放大。
5. **本质原因**：**内容质量偏差** —— 语义内容本身是对的（证据写对了、偏离原因写对了），错的是它的文本表示不满足目标格式的词法规则，导致整份文档不可解析。这类偏差不靠「更小心」避免，而靠「写后即验」把错误暴露在产生它的那一步。

## 代码示例

### ❌ 错误示例

```python
card = {
    # ❌ 值里含「英文冒号 + 空格」，未加引号
    "evidence": "见源码注释: 该分支未处理超时",
    "deviation_reason": "偏离原因: 为兼容旧接口",
}

text = "\n".join(f"{k}: {v}" for k, v in card.items())
# 生成结果：
#   evidence: 见源码注释: 该分支未处理超时
#                        ^ 解析器在此报 "mapping values are not allowed here"
yaml.safe_load(text)   # ❌ ScannerError
```

### ✅ 正确示例

```python
_YAML_SENSITIVE = set("#{}[]&*!|>%@`")


def yaml_scalar(value: str) -> str:
    """含冒号的 YAML 值一律整体加单引号（顺带处理其它敏感字符）。"""
    if ": " in value or value.endswith(":") or (_YAML_SENSITIVE & set(value)):
        return "'" + value.replace("'", "''") + "'"   # 单引号内的单引号写成两个
    return value


card = {
    "evidence": "见源码注释: 该分支未处理超时",
    "deviation_reason": "偏离原因: 为兼容旧接口",
}
text = "\n".join(f"{k}: {yaml_scalar(v)}" for k, v in card.items())

# ✅ 写后即验：不等渲染 / 机检时才报错
parsed = yaml.safe_load(text)
assert parsed == card


@pytest.mark.parametrize("value", [
    "见源码注释: 该分支未处理超时",
    "偏离原因: 为兼容旧接口",
    "（说明: 括号内的英文冒号）",
])
def test_colon_value_round_trips(value):
    assert yaml.safe_load(f"key: {yaml_scalar(value)}")["key"] == value
```

## 对应失败模式

**(h) 内容质量偏差（content_quality）**：这是生成内容的**格式性**偏差 —— 语义内容正确，文本表示不合规，导致产出的文档不可解析。它与逻辑缺陷的区别在于：没有任何计算或控制流出错，出错的是「把正确的值写进文件」这一步的表示层约束；而且同一次生成里会批量重复（本次 3 处），符合内容质量偏差「同类内容成批出现同类偏差」的特征。

**置信度说明**：0.85。YAML 的词法规则是确定的，违规立即可见（`yaml.safe_load` 直接抛 `ScannerError` / `ParserError`），判定不依赖主观标准；源记录显示同一次改动内连踩 3 处，说明这是高频模式而非偶发笔误，可预期的复现率较高。未给更高分是因为这 3 处属于同一次生成事件（`occurrences: 1`），不足以推断跨项目的出现频率。

## 改进方向

- **短期**：含冒号的 YAML 值一律整体加单引号；写入后立即用 `yaml.safe_load` 回读验证，不等渲染 / 机检时报错。
- **短期**：把「YAML 标量转义」收口到一个函数（处理冒号、引号、`#`、`{`、`[` 等敏感字符），而不是在各处手拼 `f"{k}: {v}"`。
- **长期**：在写入路径上内建解析校验（写后即验），让格式违规在产生它的那一步暴露，而不是推迟到下游消费时。
- **长期**：结构化文档统一走序列化库生成，避免手工拼接文本；对生成物的「可解析性」保留一条常驻的机检。
