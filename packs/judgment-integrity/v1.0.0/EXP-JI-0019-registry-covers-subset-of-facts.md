---
experience_id: EXP-JI-0019
category: contract_gap
pattern: "同一事实要在两处登记（来源注册表 + 显示名表）而两表各写各的、表间无一致性约束：新增字段只登记一处，读者面就露出内部字段名；注册表本身对数据字段覆盖不全时，来源区显示「来源待核」"
root_cause: |
  同一个字段要过两道登记：一道是「来源 / 日期 / 口径」，一道是「显示名」。两表独立
  维护、互相不知道对方的存在，表间没有任何一致性约束（既没有断言，也没有生成关系）。

  既有测试只断言了几个**知名**字段的显示名 —— 守门人只守着老字段，新字段天然无人
  守门。「新增字段要同步登记两处」是一条口头约定，不是一条可执行的规则。
detection_trigger: |
  - 真实产物里出现纯 ASCII 的内部字段名，作为来源表首列渲染给读者
  - 报告「来源与口径」区出现「来源待核」
  - 注册表的 key 集合与数据字段集合做差集后非空
  - 把两张表里任意一个新增 key 删掉，测试仍然全绿
fix_template: |
  1. 注册表新增 key 必须补显示名；更彻底的做法是让显示名由注册表**生成**，
     不再人工维护两份可独立变更的副本
  2. 加不变量测试：注册表的**每一个** key 经标签映射后必须含 CJK —— 断言全集，
     而不是断言几个知名条目
  3. 渲染层再兜一道：来源表每行首列断言含中文（防映射表本身漏项）
  4. 覆盖面：生成报告前把数据字段全集与注册表做**差集核对**，差集非空即失败
  5. 指向读者的文案禁用内部流程词，只写读者能懂的口径说明

  ```python
  def label_of(key):
      return SOURCE_REGISTRY[key]["label"]     # ✅ 缺登记即 KeyError，不静默回落


  def assert_registry_complete(data):
      missing = set(data) - set(SOURCE_REGISTRY)   # ✅ 覆盖面：差集非空即失败
      assert not missing, f"未登记来源的字段: {sorted(missing)}"
  ```
language: python
tags:
  - report
  - registry
  - completeness
  - i18n
  - leak
severity: high
confidence: 0.85
original_confidence: 0.5      # 导出管道默认值，非作者评估
confidence_rationale: '两种形态（只登记一处 / 一处都没登记全）同一条原理；触发信号在读者面直接可见；修法可判定（断言全集 + 渲染层兜底）'
occurrences: 1      # 合并自两条源记录，各记 1 次
audit_source: EXP-7c1962ac8d46 (+EXP-b44623638e58)
---

## 详细描述

这条经验的核心是「同一事实多处登记」：一个数据字段要同时被两处知道 ——

- **登记一**（来源 / 日期 / 口径）：这个字段从哪来、按什么口径算；
- **登记二**（显示名）：给读者看的时候它叫什么。

两表各写各的，谁也不知道谁。于是「新增字段」这件事在形式上只完成了一半，而**任何检查
都不会红**。两种形态：

**形态一：只登记了一处。** 新字段进了来源注册表，没进显示名表 → 渲染时回落成内部字段
名，读者看到的来源表首列是一串内部标识（如 `unit_price_date`、`inventory_date` 这样的
英文 key），而不是可读的中文标签。读者会把内部标识当成内容的一部分读下去。

**形态二：一处都没登记全。** 来源注册表的字段集合本身不覆盖数据里的全部字段 → 报告
来源区出现「来源待核」。这一形态更安静：它不像形态一那样露出英文，而是显示一句看起来
像「正在核」的占位文案 —— 读起来像流程状态，实际是**登记缺失**。

两种形态共同的根因是：**两处登记之间没有一致性约束**，而既有测试只断言了几个知名条目
—— 守门人守着老字段，新字段天然无人守门。「新增字段要同步登记」是口头约定，不是可执行
的规则。

## 根因链

1. **现象层**：产物里出现内部字段名，或出现「来源待核」。
2. **直接原因**：同一事实的第二处登记缺失（显示名表 / 来源注册表）。
3. **为什么会出现**：两表独立维护，既没有生成关系，也没有断言。登记一与登记二在代码里
   是两个平行的字面量字典，中间没有任何东西保证它们的 key 集合一致。
4. **为什么检查没兜住**：既有测试只断言几个**知名**条目的显示名 —— 断言的是点，不是
   集合。新字段落在断言之外，改坏了也不会红。**用「几个样本」冒充「全部条目」的断言，
   等于只给老字段配了守门人。**
5. **本质原因**：**同一事实存在两个可独立变更的副本。** 只要两处登记靠人工保持一致，
   就必然存在「只改了一处」的中间状态；而该状态在读者视野里可见（英文 key 或
   「来源待核」），在测试视野里不可见 —— 落差正好落在没人看的那一层。

## 代码示例

### ❌ 错误示例

```python
# <module>/registry.py

SOURCE_REGISTRY = {                       # 登记一：来源 / 日期 / 口径
    "unit_price_date": {"source": "<src_a>", "caliber": "报价时效判定"},
    "inventory_date": {"source": "<src_b>", "caliber": "库存口径"},
}

DISPLAY_LABELS = {                        # 登记二：显示名 —— 与登记一各写各的
    "unit_price_date": "单价日期",
    "inventory_date": "库存日期",
}


def label_of(key):
    return DISPLAY_LABELS.get(key, key)   # ❌ 缺项时静默回落 → 内部字段名原样给读者
```

```python
# <module>/report.py

def build_source_rows(data):
    rows = []
    for key in data:                          # ❌ 数据字段全集，未经注册表核对
        meta = SOURCE_REGISTRY.get(key)       # ❌ 未登记时为 None
        rows.append([label_of(key), meta["source"] if meta else "来源待核"])
    return rows
```

```python
# <module>/tests/test_labels.py

def test_labels():
    # ❌ 只断言几个知名条目 —— 新字段无人守门
    assert label_of("unit_price_date") == "单价日期"
    assert label_of("inventory_date") == "库存日期"
```

### ✅ 正确示例

```python
# <module>/registry.py

SOURCE_REGISTRY = {            # ✅ 单一事实来源：来源 / 口径 / 显示名在同一处登记
    "unit_price_date": {"source": "<src_a>", "caliber": "报价时效判定", "label": "单价日期"},
    "inventory_date": {"source": "<src_b>", "caliber": "库存口径", "label": "库存日期"},
    "<field_a>": {"source": "<src_c>", "caliber": "结算口径", "label": "<字段 A 中文名>"},
}


def label_of(key):
    return SOURCE_REGISTRY[key]["label"]      # ✅ 缺登记即 KeyError，不静默回落


def assert_registry_complete(data):
    # ✅ 覆盖面：数据字段全集与注册表做差集，非空即失败
    missing = set(data) - set(SOURCE_REGISTRY)
    assert not missing, f"未登记来源的字段: {sorted(missing)}"


def build_source_rows(data):
    assert_registry_complete(data)            # ✅ 先核对，再渲染
    return [[label_of(k), SOURCE_REGISTRY[k]["source"]] for k in data]
```

```python
# <module>/tests/test_labels.py
import re

CJK = re.compile(r"[一-鿿]")


def test_every_registered_field_has_cjk_label():
    for key in SOURCE_REGISTRY:               # ✅ 断言全集，不是几个知名条目
        assert CJK.search(label_of(key)), f"{key} 缺中文显示名"


def test_source_rows_all_chinese_labels(data):
    for row in build_source_rows(data):
        # ✅ 渲染层兜底：来源表每行首列必须含中文（防映射表本身漏项）
        assert CJK.search(row[0]), row
```

判别法：往 `SOURCE_REGISTRY` 里加一个不补显示名的 key，或从一个已有字段上删掉注册项 ——
两道断言（不变量测试 + 渲染层兜底）各应有一处变红。都不红，说明守门人只守着老条目。

## 对应失败模式

对应 `contract_gap`（契约断层）。缺的是一份**表间契约**：登记一与登记二之间「同一个 key
集合」这条约束，没有任何一侧声明它、也没有任何检查执行它。产物侧（渲染）与登记侧对
「一个字段是否可读」的理解不一致，落差直接暴露给读者 —— 这正是契约断层的形态。形态二
更进一步：注册表对数据字段的覆盖本身就是契约里没有声明的部分，于是缺口以「来源待核」
这种**看起来像状态、实际是缺失**的文案呈现。

**置信度说明**：给 0.85。两种形态来自两条源记录，原理同一条（两处登记无一致性约束）；
触发信号在读者面直接可见（内部字段名 / 「来源待核」）；修法可执行且可判定（断言注册表
全集映射后含 CJK，渲染层再断言每行首列含中文）。未给更高分是因为两条源记录各只记
1 次发生，且均未量化受影响字段在报告中的占比与下游读者的实际误读情况。

## 改进方向

**短期**：把缺失的那处登记补上；把测试从「断言几个知名条目」改为「断言注册表全集」；
来源区改用缺登记即失败的处理，而不是渲染成「来源待核」这样的占位文案。

**长期**：
- 让两处登记**同源**：显示名作为注册表条目的一部分，或由注册表生成显示名表 ——
  不再维护两份可独立变更的副本。
- 加两道兜底：不变量测试（每个 key 的显示名必须含 CJK）防登记漏项，渲染层断言
  （来源表每行首列必须含中文）防映射表本身漏项。
- 覆盖面核对做成生成前的一步：数据字段全集与注册表的差集非空即失败。**不要用占位文案
  把缺失渲染成状态** —— 读者无法区分「正在核」与「没人登记」。
- 读者面的文案禁用内部流程词，只写读者能懂的口径说明。内部流程词泄漏与英文 key 泄漏
  是同一类问题：都把内部表示当成了对外的内容。
