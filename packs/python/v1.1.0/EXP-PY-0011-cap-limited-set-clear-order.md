---
experience_id: EXP-PY-0011
category: runtime_deviation
pattern: "容量受限集合的清空写在写入之后（先 add 后 clear），清空连带删掉刚写入的条目，容量到达上限后最新条目从未被记录，is_dup 对它恒定返回 False"
root_cause: |
  达到容量上限时先 add 再检查长度并 clear，清空操作连带删除了刚 add 的条目，后续
  is_dup 检测因此对该条目失效。

  更本质的是**维护不变量的时机错了**：清空的目的不是「限制长度」，而是「为即将写入的
  条目腾位置」，所以它是写入的前置条件，不是写入后的清理。把前置条件写成后置清理，
  逻辑不会报错，只会在边界上静默丢数据。
detection_trigger: |
  - cap 边界测试：添加 cap+1 个元素后，最新元素的 is_dup 返回 False
  - 更一般的信号：容器「写入后立即可见」的隐含契约在容量边界上被违反（add(x) 之后 is_dup(x) 为假）
fix_template: |
  1. add 之前先检查 len >= cap，超限才 clear，然后再写入当前条目
  2. 用边界测试（cap+1）断言：旧条目被清、当前条目保留
language: python
tags:
  - dedupe
  - collection
  - edge-case
  - boundary
  - off-by-one
severity: medium
confidence: 0.85
occurrences: 1
audit_source: EXP-9481b412a81a
---

## 详细描述

一个容量受限的去重集合，维护逻辑写成了「先写入当前条目，再检查长度是否超限并清空」：

```python
self.items.append(key)
if len(self.items) > self.cap:
    self.items.clear()
```

当条目数达到容量上限时，这一次写入会让长度越过 `cap`，触发清空 —— 而清空把**刚刚写入的当前条目**也一并删掉了。当前条目从未被记录，于是后续 `is_dup(最新条目)` 恒定返回 `False`：去重对它完全失效。

症状有两个特征：

- **只在容量边界之后出现**：元素数远小于 `cap` 时一切正常（长度永远不越过上限，清空分支不会执行），日常使用与常规用例都看不到。
- **表现是「去重失效」而不是报错**：容器长度、写入次数等外部可见指标都正常，只有 `is_dup` 的答案在容量边界之后开始不可信。

## 根因链

1. **现象层**：容量到达上限后，最新写入的条目 `is_dup` 返回 `False`，去重静默失效。
2. **直接原因**：语句顺序错误 —— `add` 先于 `clear`，清空连带删除了刚写入的条目。
3. **为什么写成这个顺序**：直觉模型是「先把东西记下来，再看是不是装不下了」，把容量维护理解成写入**之后**的清理动作。而容量维护的真实语义是「还有位置吗？没有就腾位置」，它是写入的**前置条件**。
4. **为什么测试没发现**：只有恰好跨过 `cap` 边界的那一次写入才会命中。元素数远小于 `cap` 的用例永远看不到这个分支；要复现必须专门构造 `cap+1` 这种边界输入。
5. **本质原因**：**维护不变量的时机错误**。同一个 `clear`，写成前置条件时保证「写入的条目一定在集合里」，写成后置清理时保证的是「长度不超过 cap」—— 后者为真、前者为假，而调用方依赖的是前者。这类缺陷不产生异常，只在边界上把数据丢掉。

## 代码示例

### ❌ 错误示例

```python
class RecentSet:
    def __init__(self, cap: int):
        self.cap = cap
        self.items: list[str] = []
        self.seen: set[str] = set()

    def add(self, key: str) -> None:
        self.items.append(key)          # ❌ 先写入
        self.seen.add(key)
        if len(self.items) > self.cap:
            self.items.clear()          # ❌ 后清空：刚写入的条目一起被删掉
            self.seen.clear()

    def is_dup(self, key: str) -> bool:
        return key in self.seen


# cap=3 时加入第 4 个元素：
#   recent.add("k3")  →  len 越过 cap → clear
#   recent.is_dup("k3")  →  False   ❌ 刚写入的条目已不存在
```

### ✅ 正确示例

```python
class RecentSet:
    def __init__(self, cap: int):
        self.cap = cap
        self.items: list[str] = []
        self.seen: set[str] = set()

    def add(self, key: str) -> None:
        # ✅ 清空是写入的前置条件：先腾位置，再写入当前条目
        if len(self.items) >= self.cap:
            self.items.clear()
            self.seen.clear()
        self.items.append(key)
        self.seen.add(key)              # ✅ 当前条目一定保留

    def is_dup(self, key: str) -> bool:
        return key in self.seen


def test_boundary_cap_plus_one():
    recent = RecentSet(cap=3)
    for i in range(3):
        recent.add(f"k{i}")

    recent.add("k3")                      # 第 cap+1 个：触发清空

    assert recent.is_dup("k0") is False   # ✅ 旧条目已被清
    assert recent.is_dup("k3") is True    # ✅ 当前条目保留（这正是原实现的破绽）
```

## 对应失败模式

**(f) 运行时偏离（runtime_deviation）**：`add` 的隐含契约是「写入之后该条目立即可被查到」（否则去重集没有意义），运行时行为在容量边界上违反了这个契约 —— `add("k3")` 返回后 `is_dup("k3")` 仍为 `False`。契约没有失效，失效的是实现；偏离只在 `cap` 边界这一窄输入域上显现，因此 spec 与运行时行为在日常路径上看起来完全一致。

**置信度说明**：0.85。边界用例（`cap+1`）可精确复现，不依赖时序、环境或并发；「先 `add` 后 `clear`」是纯逻辑缺陷，读代码即可确认因果链，没有解释空间。未给更高分是因为 `occurrences: 1`，且源记录未展开该去重集失效之后的下游影响（是否产生了重复处理、重复量级如何）。

## 改进方向

- **短期**：`add` 之前先检查 `len >= cap`，超限才 `clear`，之后再写入当前条目；用 `cap+1` 边界用例断言「旧条目被清、当前条目保留」。
- **短期**：对容量受限容器统一补三类边界用例 —— 恰满、超一个（`cap+1`）、清空后立即查询最新条目。
- **长期**：把「容量维护」在 API 设计上表达为写入的前置步骤（如 `ensure_capacity()` 与写入分开命名），避免它被误读成写入后的清理。
- **长期**：为「写入后立即可见」这类隐含契约补不变量断言（`add(x)` 之后 `is_dup(x)` 必须为真），让容器类的不变量可被测试直接守护。
