---
experience_id: EXP-PY-0009
category: runtime_deviation
pattern: "guard 仅记录违规不拦截输出：验证结果作为元数据返回后，调用方丢弃 guard 字段，违规回复仍原样到达用户（fail-open）"
root_cause: |
  验证层与输出层解耦不完整：guard 返回 {ok, issues}，但 service 只透传 text 字段，
  未消费 guard 去决定「拒绝还是替换」；与规格中「拦截」类语义（THEN/AND 描述的强制后果）
  不一致。

  「解耦」本身是把校验逻辑独立出来的好设计，但两侧之间缺一份**消费契约**：没有任何地方
  规定「验证结论必须以什么方式影响输出路径」。于是 ok/issues 退化成了纯观测元数据 ——
  能被记录、能被打印，就是不参与决策。规格里的模态词（必须拦截）在实现里被降级成了
  陈述句（记录了问题）。
detection_trigger: |
  - 检查项：guard / 验证函数返回的 ok / issues 是否被调用方**实际消费**（而不是只被赋值）
  - 违规回复仍进入最终输出：LLM 自答含情绪词、虚构数字、或未走工具仍原样到达用户
  - 验证函数跑了、日志里有 issues，但输出与不跑时完全一致
fix_template: |
  1. 验证结果必须 fail-closed 消费
  2. blocking 违规（情绪词 / 虚构数字 / 未走工具）→ 替换回复为拒绝文案并标记 blocked
  3. 仅「缺数据基准」类 → 自动补齐标注，不拦截
  4. 测试断言违规原文不进入最终 answer
language: python
tags:
  - guard
  - fail-closed
  - fail-open
  - llm-safety
severity: critical
confidence: 0.85
occurrences: 1
audit_source: EXP-a58efb79ca69
---

## 详细描述

链路里存在一个 guard（验证函数），它会检查回复文本并返回 `{ok, issues}`。这个函数**确实被执行了**，也确实发现了问题 —— 但它的返回值只作为元数据向上传递，调用方（service 层）只把 `text` 透传给输出路径，从未根据 `ok` / `issues` 决定「拒绝」还是「替换」。

结果是：含情绪词、含虚构数字、或未走工具的 LLM 自答，**原样到达用户**。

这是 fail-open 的教科书形态 —— 防线默认是开的，只有显式关闭才会拦住东西，而没有任何一处代码显式做了这件事。它比「没有检查」更隐蔽：

- 日志里能看到 guard 跑了；
- 日志里能看到 `issues` 非空；
- 如果只看「验证是否被调用」的测试，它是通过的。

但输出行为与完全不做校验时**一模一样**。检查存在 ≠ 防线存在：真正的安全属性不来自「检查被执行」，只来自「检查结论被强制消费」。

而且这与规格不符：规格用「拦截」类语义（THEN/AND 描述的强制后果）写这个检查点，实现的语义是「记录」。两者方向相反。

## 根因链

1. **现象层**：违规回复原样到达用户，机制上没有任何报错或异常。
2. **直接原因**：guard 返回了结论，service 没有消费它 —— 只透传 `text`。
3. **为什么会出现**：验证层与输出层**解耦不完整**。把校验独立出来是对的，但脱离了同一处代码之后，必须补一份显式的「消费契约」，规定验证结论如何影响输出路径；这份契约缺失时，`ok` / `issues` 自然退化为观测数据 —— 它被返回、被记录、被传递，却不参与任何决策。**没有任何一行代码出错**，只是没有任何一行代码负责拦截。
4. **为什么规格没兜住**：规格写的是「拦截」类语义（强制后果），实现提供的是「记录」。规格里的模态词在翻译成代码时丢了 —— 描述「必须阻止 X 到达用户」比描述「检查 X」难得多，于是实现停留在了较容易的那一半。
5. **本质原因**：**fail-open 是缺省状态**。任何校验系统在没有任何显式拦截代码时都是开放的；要获得 fail-closed 属性，必须有一处代码显式地把「违规」翻译成「拒绝输出」。安全性只能由那个翻译步骤提供，不能由检查步骤提供。

## 代码示例

### ❌ 错误示例

```python
@dataclass
class GuardResult:
    ok: bool
    issues: list[str]


def validate_reply(text: str) -> GuardResult:
    issues = []
    if has_emotion_words(text):
        issues.append("emotional_words")
    if has_fabricated_numbers(text):
        issues.append("fabricated_numbers")
    if not used_tools():
        issues.append("tool_not_used")
    return GuardResult(ok=not issues, issues=issues)


def respond(user_input: str) -> str:
    text = llm.generate(user_input)
    guard = validate_reply(text)   # ❌ 执行了，但结论未被消费
    return text                    # ❌ 违规原文原样返回给用户（fail-open）
```

### ✅ 正确示例

```python
BLOCKING = frozenset({"emotional_words", "fabricated_numbers", "tool_not_used"})
REFUSAL_TEMPLATE = "抱歉，我无法基于当前依据回答这个问题。"


@dataclass
class Reply:
    text: str
    blocked: bool
    issues: list[str]


def respond(user_input: str) -> Reply:
    text = llm.generate(user_input)
    guard = validate_reply(text)

    blocking = BLOCKING & set(guard.issues)
    if blocking:
        # ✅ fail-closed：违规原文绝不进入最终回复
        return Reply(text=REFUSAL_TEMPLATE, blocked=True, issues=guard.issues)

    if guard.issues:
        # ✅ 仅「缺数据基准」类：补齐标注，不拦截
        return Reply(text=annotate(text, guard.issues), blocked=False, issues=guard.issues)

    return Reply(text=text, blocked=False, issues=[])


def test_blocking_violation_never_reaches_answer():
    violating_text = make_reply_with_fabricated_numbers()
    reply = respond("some input")     # 桩：llm.generate 返回 violating_text
    assert reply.blocked is True
    assert violating_text not in reply.text   # ✅ 断言违规原文不进入最终 answer
```

## 对应失败模式

**(f) 运行时偏离（runtime_deviation）**：规格以「拦截」类语义（THEN/AND 描述的强制后果）声明该检查点，运行时的实际行为是「仅记录、不拦截」。spec 与运行时行为方向相反 —— 规格说「违规内容不得到达用户」，运行时说「违规内容已到达用户」，而验证函数的存在让两者看起来是同一件事。这不是功能没实现，而是实现与规格在**模态**上偏离（必须 → 可选）。

**置信度说明**：0.85。fail-open 属于安全类缺陷，方向明确、无需权衡；修复方案落在一条可直接落地且可判定的测试上（断言违规原文不进入最终 `answer`），不依赖主观判断；blocking / 非 blocking 的分类也已在源记录中给出。未给更高分是因为 `occurrences: 1`，且三类 blocking 违规各自的实际发生率与真实影响面在源记录中未量化。

## 改进方向

- **短期**：验证结论必须 **fail-closed 消费** —— blocking 违规（情绪词 / 虚构数字 / 未走工具）替换回复为拒绝文案并标记 `blocked`；仅「缺数据基准」类自动补齐标注，不拦截。
- **短期**：用「违规原文不进入最终 `answer`」作为断言，而不是断言「guard 被调用过」；后者无法区分 fail-open 与 fail-closed。
- **长期**：把「检查结论是否被消费」纳入评审清单 —— 检查存在 ≠ 防线存在，凡引入校验函数必须同时给出消费点。
- **长期**：在验证层与输出层之间建立结构化契约，把 blocking / 非 blocking 分类作为类型的一部分，而不是散落在字符串列表里；默认按 fail-open 风险处理任何新校验点。
