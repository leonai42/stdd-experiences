---
experience_id: EXP-PYT-0001
category: coverage_vacuum
pattern: "多模块 `--cov` 覆盖测量触发 numpy 二次加载 → numpy 聚合测试集体假红（`int() ... not '_NoValueType'`），而无覆盖全量回归全绿"
root_cause: |
  coverage 的 source 插桩与 numpy 的导入时序冲突。当覆盖目标写成**模块级**（`--cov=<package>.<module>`）时，
  coverage 走 `source_pkg` 预导入路径，在 pytest 导入任何测试之前先把被测包导进来；numpy 因此在
  coverage 启动之后才被导入，numpy 的 `__init__` 会跑第二次，pandas 随即打印
  `The NumPy module was reloaded` 警告。

  二次加载出的 numpy 实例中，`_NoValue` 哨兵对象的身份与 C 层 `umr_sum` 内部识别的哨兵不一致；
  `numpy/_core/_methods._sum` 在掩码聚合路径（`mask.sum()` → `nanvar` / `_get_counts`）把这个哨兵
  当作真实数值传入，最终在 `int(_NoValue)` 处抛 TypeError。

  关键点：**触发面是覆盖测量本身，不是被测代码**。同一份代码在无覆盖模式下全部通过；
  `pytest-cov` 与 `coverage run` 一致复现。判别法：把本次**从未改动过**的文件交给同样的覆盖命令，
  若能复现即证明与本次改动无关。

  实测规模：一次多模块测量表现为 18 例 numpy 聚合测试失败、332 例通过；同一代码无覆盖 350 例全绿。
  包级目标（`--cov=<package>`）与模块级目标的对照是决定性的：同文件、同用例，包级全绿、模块级必红。
detection_trigger: |
  - `pytest --cov=<package>.<module>` 多模块测量时，numpy 聚合类测试（标准差 / 方差 / 求和，以及若干
    指标与因子类计算）集体失败，报 `int() ... not '_NoValueType'`
  - 同一批用例去掉覆盖、按无覆盖全量回归（`pytest tests/`）跑则全绿
  - 失败输出伴随 `The NumPy module was reloaded` 警告
  - 同一条用例裸跑通过、加 `--cov` 必失败，且失败发生在与本次改动**无关**的文件里，看起来像回归
  - 覆盖报告的汇总数字与用例汇总数字对不上（覆盖运行失败数 ≠ 无覆盖运行失败数）
fix_template: |
  1. 以无覆盖全量回归 `pytest tests/` 为权威质量门；覆盖率测量单独进行，不受假红干扰。
  2. 覆盖测量报数时，若测量运行含聚合测试假红，报告中必须标注"测量受 numpy 双加载缺陷影响，非代码
     回归"，并附无覆盖复跑证据。
  3. 不要在 conftest 预导入 numpy/pandas 规避——实测无效（coverage 插桩 finder 会绕过 sys.modules
     缓存对 numpy 子模块二次加载）。
  4. 判定回归前，先在无覆盖模式复跑失败用例；全绿即工具缺陷，不是代码缺陷。
  5. 新增 numpy 聚合相关测试后，须同时验证无覆盖运行通过，避免把假红误记为回归。
  6. 覆盖目标粒度优先用包级 `--cov=<package>` 替代模块级 `--cov=<package>.<module>`：包级不触发
     `source_pkg` 预导入路径，同文件同用例全绿（实测边界）。
  7. 判别"是否与本次改动相关"：换成本次未改动的文件做同样覆盖，若能复现即与改动无关。
  8. 证据缺口如实披露（例如"未做 HEAD 回退复跑"），不要用"大概无关"蒙过去。
language: python
tags:
  - coverage
  - numpy
  - test-infra
  - false-positive
  - pytest-cov
severity: medium
confidence: 0.90
occurrences: 1
audit_source: EXP-2026-0026 (+EXP-21eb86ed5cc0)
---

## 详细描述

一次多模块覆盖率测量中，numpy 聚合类测试集体翻红：18 例失败、332 例通过，全部报
`int() argument must be a str/bytes-like object or a real number, not '_NoValueType'`。同一份代码、
同一条命令去掉覆盖后按无覆盖全量回归跑——350 例全绿。这一组对照说明失败与业务代码无关，
是覆盖测量本身引入的。

后续在同一仓库的另一处复现把边界钉得更细：

- `--cov=<package>.<module>`（**模块级**目标）——把该模块当作 `source_pkg` **预导入**。若该模块间接
  导入 numpy，numpy 的 `__init__` 就跑两次，`The NumPy module was reloaded` 警告必现；随后 pandas 的
  聚合路径抛 TypeError。**用本次 change 从未碰过的文件做目标同样复现**。
- `--cov=<package>`（**包级**目标）——不触发这条预导入路径，同一个文件、同一条用例全绿。

两个信号的组合足以定性：**裸跑通过 + 加 `--cov` 必失败 + 伴随 numpy reloaded 警告 = 工具缺陷**，
而不是代码回归。失败之所以"看起来像回归"，是因为它落在与本次改动无关的文件里，而覆盖命令又是
团队的标准做法，没人会第一时间怀疑测量工具。

## 根因链

1. **直接原因**：多模块覆盖测量让 numpy 被加载两次，聚合路径拿到身份不一致的 `_NoValue` 哨兵。
2. **机制层**：`--cov=<package>.<module>` 触发 coverage 的 `source_pkg` 预导入——在 pytest 导入测试
   之前先导入被测包，改变了 numpy 的导入时序；coverage 的插桩 finder 又会绕过 `sys.modules` 缓存对
   numpy 子模块做二次加载，所以"在 conftest 里先导入 numpy"这条直觉修法实测无效。
3. **为什么是"集体失败"而不是零星失败**：受影响的聚合测试共享同一条掩码求和路径
   （`mask.sum()` → `nanvar` / `_get_counts`），哨兵被当作真实值传入的那一刻，这一整类用例同时倒下。
4. **为什么没被当场识破**：失败出现在与改动无关的文件里，且"加了覆盖命令才红"很容易被读成
   "覆盖测量更严格，暴露了真实问题"——因果方向被倒置。
5. **为什么证据链也没兜住**：把测量运行的失败数直接当成回归数上报，缺少"无覆盖复跑"这一道判别，
   于是一个工具缺陷被写进了回归清单。

## 代码示例

### ❌ 错误示例

```bash
# 模块级覆盖目标：触发 source_pkg 预导入 → numpy 二次加载
pytest --cov=<package>.<module> tests/

# 输出（节选）：
#   The NumPy module was reloaded ...
#   18 failed, 332 passed
#   TypeError: int() argument must be a str/bytes-like object or a real number,
#              not '_NoValueType'
```

```python
# 反模式：把测量运行的失败数直接写成回归结论
report = {
    "coverage_run": "18 failed / 332 passed",
    "verdict": "本次改动引入 18 处回归",       # ← 未做无覆盖复跑，因果倒置
}
```

```python
# 反模式：想靠 conftest 预导入规避（实测无效）
# conftest.py
import numpy   # noqa: F401  —— coverage 插桩 finder 会绕过 sys.modules 缓存，
import pandas  # noqa: F401     对 numpy 子模块二次加载，问题照旧
```

### ✅ 正确示例

```bash
# 1) 权威质量门：无覆盖全量回归
pytest tests/                     # 350 passed —— 结论以这一条为准

# 2) 覆盖测量单独跑，目标用包级而非模块级
pytest --cov=<package> tests/     # 不触发 source_pkg 预导入，同文件同用例全绿

# 3) 判别法：把失败用例在无覆盖模式下复跑
pytest tests/test_aggregates.py               # 全绿 → 工具缺陷，不是代码缺陷
pytest --cov=<package>.<module> tests/test_aggregates.py   # 必红 → 覆盖测量副作用
```

```python
# 覆盖测量报告的写法：把"测量不可信"显式写进结论，并附证据
report = {
    "measurement_run": "18 failed / 332 passed",
    "no_coverage_rerun": "350 passed",          # 复跑证据
    "note": "测量受 numpy 双加载缺陷影响，非代码回归",
    "root_cause": "coverage source_pkg 预导入 + numpy 二次加载（工具缺陷）",
    "not_related_to_change": "用本次未改动的文件做同样覆盖同样复现",
    "evidence_gap": "未做 HEAD 回退复跑",        # 缺口如实披露
}
```

## 对应失败模式

**(j) 覆盖真空（coverage_vacuum）**。这一条的表层是"命令粒度用错"（容易被读成 `tool_misuse`），但实质
后果是**覆盖测量这条证据链整体不可采信**：测量运行混进 18 例假红，既不能据此判断真实覆盖，也不能
据此判断回归；要恢复证据必须换覆盖目标粒度、把测量与质量门分离、并补一次无覆盖复跑。被破坏的是
"覆盖证据"本身，所以按覆盖真空归类，而不是按工具误用。两者的修复动作也不同：工具误用的修复是
"改命令"，覆盖真空的修复是"重建证据链 + 标注测量不可信"。

**不适用场景（反例）**：若失败用例**裸跑也失败**，或失败集中在本次改动直接触及的模块、且无
`The NumPy module was reloaded` 警告，则这是真实回归，本条不适用——必须先做无覆盖复跑再套用。

**置信度说明**：0.90 —— 对照充分且方向明确：18 例失败 vs 无覆盖 350 全绿是同一代码的两组实测，
包级 / 模块级目标在同文件同用例上全绿 / 必红构成第二次独立对照；并给出了「先无覆盖复跑再判回归」
这一可直接执行的判别法。未给更高分，是因为触发条件绑定 numpy 版本与 coverage 插桩实现，跨版本
或换用其他测量方式时需要重新确认边界。

## 改进方向

- **短期**：把质量门分层——无覆盖全量回归是唯一权威门，覆盖率测量单独跑；覆盖目标统一改成包级
  `--cov=<package>`；CI 中 numpy 聚合测试的失败一律先无覆盖复跑再定性。
- **长期**：在覆盖测量脚本里内置"双加载检测"——捕获到 numpy reloaded 警告即把本次测量标记为
  不可信，并自动追加一次无覆盖复跑；把「工具缺陷 vs 代码缺陷」的分诊流程写进测试基础设施文档，
  避免下一次仍靠个人经验判断。
