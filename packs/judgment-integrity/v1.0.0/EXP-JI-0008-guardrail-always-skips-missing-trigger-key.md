---
experience_id: EXP-JI-0008
category: coverage_vacuum
pattern: "流程末端才生效的护栏，其触发键没有任何地方要求声明 —— 于是该护栏对每一个变更恒 SKIP，而 SKIP 在计数里和 PASS 一样不刺眼"
root_cause: |
  护栏的触发条件依赖一个从未纳入「创建」动作的键：末端步骤只在变更记录里声明了
  该键（这里是一段「交付后复跑全量测试所用的命令」）时才执行，而变更模板与初始化
  动作从不写这个键。没有人负责写下它，也没有任何一步问过「谁负责写下它」。

  「不适用」与「未配置」走了同一条出口：护栏没跑与护栏跑过，在输出里都表现为一个
  安静的 SKIP，而 SKIP 与 PASS 在计数里并列展示、同样不刺眼。护栏的触发条件因此
  退化成一个恒假条件，退化后的形态与成功形态在读者眼里无法区分。
detection_trigger: |
  - 交付摘要出现「交付后复跑: [SKIP] 未声明 <触发键>」
  - 同一仓库的历史变更**全部**是同样的 SKIP —— 全部 SKIP 是系统性信号：该护栏自
    上线以来从未生效过，而不是某几次变更恰好不适用
  - 计数里 SKIP 与 PASS 混在同一栏，没有任何「这是护栏失效」的标记
fix_template: |
  两条路，任选其一但必须选一条：
  1) 由创建侧补齐：在变更模板 / 初始化动作里写入触发键，并让「创建即声明」类检查
     核它在场 —— 键不存在时创建动作本身就该失败；
  2) 由判据侧区分：让 SKIP 显式分成「不适用」与「未配置」两种，并在交付摘要里分别
     计数；「未配置」计入护栏失效，不与 PASS 同栏。
  另外：凡「末端生效、输入来自开端」的护栏，都必须指名道姓地写出「谁负责写下这个键」。
language: python
tags:
  - guardrail
  - silent-skip
  - missing-key
  - delivery-gate
  - coverage-vacuum
severity: high
confidence: 0.85
occurrences: 1
audit_source: EXP-b157d2d776c9
original_confidence: 0.5      # 导出管道默认值，非作者评估
confidence_rationale: '触发信号明确（摘要 SKIP 行 + 历史全 SKIP）；修法二选一可直接落地；全量「所有变更都没声明过」为源记录观察，未附可复算统计'
---

## 详细描述

有一类护栏**在流程末端才生效**：交付或归档时复跑全量测试，只有在变更记录里声明了
「用哪条命令跑」时才真正执行。这条护栏本身是合理的 —— 让末端复跑用变更自己的命令，
比让末端猜一个全局命令更可靠。问题出在它的输入：**触发键位于流程开端，而开端没有任何
地方要求声明它**。

于是护栏的触发条件从不成立：本仓所有变更都没声明过这个键，护栏对每一个变更都走
「未声明 → SKIP」。它安静地出现在摘要里，与「本变更不需要末端复跑」在输出上完全
一样。SKIP 与 PASS 在计数里并列展示、同样不刺眼 —— 一条从未生效过的护栏，就此
在报表上取得了与生效护栏相同的外观。

这条经验的一般形态是：**护栏的触发条件依赖一个没有生产者的键，而「没跑」与「跑了
且通过」在观测面上不可区分**。它和「判据永不返回失败」是同一族问题的另一种成因：
前者是判据的取值域里没有那个值，后者是判据的输入里从来没有那个键 —— 结果都是
一份看起来在场、实则从未生效的保障。

检测这类问题最省力的信号是**全量视角**：个别变更 SKIP 可以是正常的（确实不适用），
但**全部变更都 SKIP** 只能有一种解释 —— 该护栏从未生效过。这个信号廉价且不需要
读实现：对同一仓库的历史输出做一次全量统计即可。

## 根因链

1. **现象层**：交付摘要里末端复跑一栏恒为 SKIP，每一份变更记录都是如此。
2. **直接原因**：触发键从未被写下；护栏在键缺失时走 SKIP 出口。
3. **为什么键从未被写下**：键的消费者在流程末端，而键的生产者本应在流程开端（变更
   模板 / 初始化动作），开端从不生成它。**没有任何一处指名道姓地写着「谁负责写下它」**
   —— 这类缺口在职责分工里没有归属，于是谁都不写。
4. **为什么长期没人发现**：SKIP 被当作正常态，而不是「护栏失效」。它既不是失败
   （不会让交付变红），也不占用任何人的注意力（与 PASS 同栏、同样安静）。在
   「不适用」与「未配置」共用一条出口的设计下，「护栏没跑」这件事没有任何观测面。
5. **本质原因**：**护栏的触发条件被当成了外部输入，而不是护栏自身交付物的一部分**。
   一条护栏要成立，必须同时交付三样东西：判据本身、它的输入从哪来、以及输入缺失时
   算不算失败。这里三样只交付了第一样 —— 缺失的那两样恰好是决定护栏是否生效的两样。

## 代码示例

### ❌ 错误示例

```python
def post_delivery_rerun(change) -> Result:
    cmd = change.declaration.get("<trigger_key>")
    if not cmd:
        # ❌ 「不适用」与「未配置」共用同一条出口；缺键被当成正常态
        return Result(status="SKIP", reason="未声明 <trigger_key>")
    return Result(status="PASS" if run(cmd) else "FAIL")


def summarize(results) -> dict:
    # ❌ SKIP 与 PASS 并列计数，没有任何「护栏失效」的标记
    return dict(collections.Counter(r.status for r in results))


# 变更模板 / 初始化动作里从来没有 <trigger_key> 这一项 —— 没人负责写下它
```

### ✅ 正确示例

```python
class SkipReason(str, Enum):
    NOT_APPLICABLE = "NOT_APPLICABLE"     # 本变更确实不需要末端复跑
    NOT_CONFIGURED = "NOT_CONFIGURED"     # ✅ 护栏失效：没人写下触发键


def post_delivery_rerun(change) -> Result:
    cmd = change.declaration.get("<trigger_key>")
    if cmd is None:
        return Result(status="SKIP", reason=SkipReason.NOT_CONFIGURED)   # ✅ 可区分
    return Result(status="PASS" if run(cmd) else "FAIL")


def check_trigger_key_declared(change) -> None:
    # ✅ 创建即声明：模板/初始化动作必须写下触发键，检查核它在场
    if "<trigger_key>" not in change.declaration:
        raise DeclarationError(
            "触发键未声明 —— 末端复跑护栏将恒 SKIP；请在变更创建时写下它"
        )


def summarize(results) -> dict:
    counts = dict(collections.Counter(r.status for r in results))
    unconfigured = [r for r in results if r.reason is SkipReason.NOT_CONFIGURED]
    if unconfigured:
        # ✅ 「未配置」计入护栏失效，不与 PASS 同栏
        counts["GUARDRAIL_INEFFECTIVE"] = len(unconfigured)
    return counts


def test_guardrail_actually_ran_at_least_once(history):
    # ✅ 「全部 SKIP」本身就是失效证据，而不只是安静的一栏
    assert any(r.status in ("PASS", "FAIL") for r in history), (
        "该护栏在全部历史变更上都是 SKIP —— 它从未生效过"
    )
```

如果选的是「创建侧补齐」这条路，那么判断标准很直接：**手工造一个不含触发键的变更，
创建动作应当失败**；如果它能创建成功，触发键就仍然没有生产者。

## 对应失败模式

**(j) 覆盖真空（coverage_vacuum）**：判据（末端复跑）存在、被调用、也输出了结果，
但它对**任何**输入都不进入「真的跑一遍」的分支 —— 覆盖真空的另一种形态：不是没有
护栏，而是护栏的触发条件恒假。它与「判据永不返回失败」同族：一个是取值域缺值，
一个是输入恒缺键，结果都是零执行。

不归 `contract_gap`：这里没有两侧对同一契约的不同理解；触发键的消费者写得很清楚，
缺的是**生产者**（谁写下它）与**缺失语义**（没写下算不算失败）。这是链路断在护栏
内部的形态，不是两侧理解分歧。

**置信度说明**：给 0.85。触发信号非常具体（摘要里的 SKIP 行、历史全 SKIP、SKIP 与
PASS 同栏），修法两条路径都可直接落地（创建侧核键在场 / SKIP 分类 + 未配置计入失效），
且「全部 SKIP = 从未生效」这一判据不需要读实现就能算出来。扣分项：其一，源记录
`occurrences: 1`，单次发生；其二，「本仓所有变更都没声明过这个键」是源记录的**观察
结论**，未附可复算的全量统计 —— 使用本条前请先对自己的仓库做一次全量统计（SKIP 计数
是否等于变更总数），**待复核**；其三，源记录未给出末端护栏的其余实现细节，示例代码
为示意写法，触发键以 `<trigger_key>` 占位。

## 改进方向

**短期**：
- 对历史输出做一次全量统计：SKIP 数是否等于变更总数。相等即该护栏从未生效，不必
  再读实现。这条统计是零成本的，任何「末端护栏」都值得先做一遍。
- 二选一落实修法：要么在变更模板 / 初始化动作里写入触发键并让检查核它在场，要么让
  SKIP 分成「不适用」与「未配置」两类、且「未配置」计入护栏失效。
- 摘要不得把「没跑」与「跑过且通过」并列：两者在观测面上的区别，是这条护栏能否
  被发现的唯一依据。

**长期**：
- 凡「末端生效、输入来自开端」的护栏，其输入键必须在创建动作里被强制生成 —— 让
  「缺键」在流程开端就报错，而不是在末端安静地退化。
- 把「全部 SKIP」做成系统性告警：一个在全部输入上都不生效的护栏，等价于一条永远
  为绿的判据，应当在报表层面被单独标出，而不是混进状态计数。
- 交付一份护栏时必须同时给出它的三样东西：判据本身、输入的来源、输入缺失时的语义。
  缺任何一样，这条护栏就还没有交付完成。
