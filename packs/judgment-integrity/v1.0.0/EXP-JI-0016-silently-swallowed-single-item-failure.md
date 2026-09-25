---
experience_id: EXP-JI-0016
category: coverage_vacuum
pattern: "批处理把「单个坏输入不该阻断整批」写成「单个坏输入不留痕迹」：被吞掉的输入既不计数也不留名，汇总数字静默变小；同一写法落在验证对象的装载上时，静默缩小的是验证范围，判据仍写「通过」"
root_cause: |
  「单个坏输入不该阻断整批」被写成了「单个坏输入不留痕迹」—— 容错与可观测性被当成
  二选一，跳过的那条既不计数也不留名；而失败分支上没有任何断言，于是「跳过」与
  「成功」在观测面上完全等价。

  更根本的一层：这批代码把「数到了几个」当成了「应该有几个」的答案。计数从上游输入
  推导而来，某条输入被丢弃只会让汇总值跟着变小，而没有任何独立的「应有条数」参照点 ——
  少掉的那几条不会让任何东西变红。
detection_trigger: |
  - 汇总数字与它的字面量来源对不上（把源文件里那类条目数一遍即可发现）
  - 某份输入在计数里贡献恒为 0，或某份输入从未出现在任何输出里
  - 报错 / 跳过路径上没有任何一条测试；把该分支改成永远通过，测试不会红
fix_template: |
  1. 「没数到」记 null，不记 0 —— 0 是「数了，是零」，两者在报告里必须可区分
  2. 被跳过的输入必须把 **文件名 + 原因（含行号）** 写进一个**机器可读**的位置
     （结构化的 skipped 列表，而不是日志里的一行人话）
  3. 该位置必须有**读取方**（检查项 / 断言），否则与没写等价
  4. 变异验证：把「读取方」改成永远通过，确认测试会红

  ```python
  def load_all(paths):
      items, skipped = [], []
      for p in paths:
          try:
              items.extend(parse(p))
          except Exception as exc:        # ✅ 容错：单个坏输入不阻断整批
              skipped.append(SkipRecord(path=p, reason=repr(exc),
                                        line=getattr(exc, "lineno", None)))
      return items, skipped                # ✅ 记账：跳过不丢


  def assert_no_skips(skipped):
      if skipped:                          # ✅ 有读者：跳过即为失败
          raise AssertionError(f"{len(skipped)} 份输入被跳过: {skipped}")
  ```
language: python
tags:
  - silent-skip
  - batch-resilience
  - observability
  - count-mismatch
severity: high
confidence: 0.85
original_confidence: 0.5      # 导出管道默认值，非作者评估
confidence_rationale: '同一形态在同一批代码里出现两处（汇总计数与验证范围）；有「字面量对账」这一便宜的判别法，且含可执行的变异验证'
occurrences: 1
audit_source: EXP-c20d42371e69
---

## 详细描述

批处理循环里一个 `except Exception: continue`（或等价的静默跳过）有两副面孔，而它们
常被同一句话辩护：「单个坏输入不该阻断整批」。这句话是对的，问题是它被实现成了
「单个坏输入不留痕迹」。

**第一副面孔是数字**：汇总值静默变小。现场是：汇总记录里写着 22 条，而源文件里这类
条目按字面量数有 26 条 —— 差的 4 条来自一份 YAML 解析失败（值里含 `: `、少打了一对
引号，报错落在第 43 行），被整份丢弃。当时全量 1038 条测试全绿、检查项 0 个失败，
发现它的是**人把两个数对了一下**。

**第二副面孔是范围**：同一行写法落在「验证对象」的装载上时，静默缩小的不是数字而是
验证范围 —— 损坏的那份规格里声明的条目从验证清单里消失，而验收条目**照样写「通过」**。
数字少算是「报告不准」；验证范围缩小而报通过是「证据不成立」。后者更严重：报告不准
只是描述失真，证据不成立则是结论本身不成立。

两者的共同点是：容错做对了（整批没被一个坏输入拖垮），可观测性做没了（没人知道跳过了
什么）。**正确的形态不是「跳过」，而是「跳过 + 记账 + 有读者」。** 账要记在机器读得到
的地方，还要有一个读取方 —— 否则那份账和没记一样。

## 根因链

1. **现象层**：汇总数字比源文件里的字面量条目少；或某份输入整份没有进入验证清单，
   而验收结论仍是「通过」。
2. **直接原因**：`except Exception: continue` 把失败输入整份丢弃，跳过分支既不计数
   也不留名。
3. **为什么会出现**：「单个坏输入不该阻断整批」这个正确的容错需求，被实现成了
   「单个坏输入不留痕迹」。容错与可观测性被当成二选一 —— 而它们本是两个正交的需求：
   跳过是为了让流程走下去，记账是为了让跳过可见。
4. **为什么检查没兜住**：汇总值从**输入**推导而来，丢弃一条输入只会让汇总值变小，
   而没有任何独立的「应有条数」参照点。同时跳过路径上没有任何断言 —— 把这条分支改成
   永远通过，测试不会红，于是它在观测面上与成功等价。
5. **本质原因**：把「数到了几个」当成了「应该有几个」。缺少一个与主流程独立的对账点
   （字面量来源、集合差集、覆盖清单），数字的变化就没有任何东西来核对。

## 代码示例

### ❌ 错误示例

```python
# <module>/batch.py

def load_all(paths):
    items = []
    for p in paths:
        try:
            items.extend(parse(p))     # parse 内部做 YAML / JSON 解析
        except Exception:
            continue                   # ❌ 跳过且不留痕迹：不计数、不留名、无人读
    return items                       # ❌ 返回值看不出「少了几份」


def build_summary(paths):
    items = load_all(paths)
    return {"total": len(items)}       # ❌ 汇总值随输入静默变小，且无参照点
```

把这段的 `except` 分支改成 `pass`、或改成永远成功，任何测试都不会变红 —— 跳过路径上
没有任何断言。

### ✅ 正确示例

```python
# <module>/batch.py
from dataclasses import dataclass


@dataclass(frozen=True)
class SkipRecord:
    path: str
    reason: str
    line: int | None = None


def load_all(paths):
    items, skipped = [], []
    for p in paths:
        try:
            items.extend(parse(p))                 # ✅ 容错：单个坏输入不阻断整批
        except Exception as exc:
            skipped.append(SkipRecord(             # ✅ 记账：文件名 + 原因 + 行号
                path=p, reason=repr(exc), line=getattr(exc, "lineno", None)
            ))
    return items, skipped


def build_summary(paths):
    items, skipped = load_all(paths)
    return {
        "total": len(items),
        "skipped_total": len(skipped),             # ✅ 「已数到」与「未数到」分开报
        "skipped": [s.__dict__ for s in skipped],  # ✅ 机器可读，别只写日志
    }


def assert_no_skipped(summary):
    # ✅ 有读者：机器可读的账必须有人查，否则与没写等价
    assert summary["skipped_total"] == 0, summary["skipped"]
```

两种用法都要用到这份账：装载「被统计的对象」时，账驱动**计数对账**；装载「被验证的
对象」时，账驱动**拒绝给出通过结论** —— 少了条目就不允许写「通过」。

判别法（可执行）：把 `assert_no_skipped` 换成 `pass`，再让其中一个输入文件解析失败 ——
若测试仍全绿，说明这份账没有读者。

## 对应失败模式

对应 `coverage_vacuum`（覆盖真空）。形似 `cascading_errors`（坏输入波及下游）但不是：
坏输入**没有**波及下游，恰恰相反，这一点被做过头了。真正的缺口在覆盖 —— 跳过路径，
以及「应有条数 vs 实际条数」的对账，没有任何判据覆盖，于是流程的失败分支在观测面上
不存在。第二处用法更进一步：被静默缩小的是验证范围本身，判据却仍输出「通过」，这时
缺的不再是数字，而是证据。

**置信度说明**：给 0.85。触发信号明确（两个数字对不上、字面量可数），判别法可执行
（把读取方改成永远通过，看测试是否变红），且同一形态在同一批代码里出现两处（汇总计数
与验证范围），互为佐证。未给更高分是因为 `occurrences: 1`（同一次改动内的两处），
且源记录未量化缺失条目在下游造成的实际影响面。

## 改进方向

**短期**：把那个 `except Exception: continue` 改成「跳过 + 记账 + 有读者」三步；缺失值
报 `null` 而不是 0；跳过记录含文件名、原因与行号。

**长期**：
- 给每个批处理装载点配一个**独立对账点**（源文件字面量条数、集合差集、覆盖清单），
  让「应有几条」不只从输入推导。
- 把「跳过路径是否可观测」纳入评审清单：凡写 `continue` / `pass` / 空 `except`，
  须同时给出记账位置与读取方。
- 用变异验证守住这条经验：把读取方改成永远通过，测试必须变红；不红说明账没有读者。
