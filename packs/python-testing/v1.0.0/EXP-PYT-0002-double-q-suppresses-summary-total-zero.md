---
experience_id: EXP-PYT-0002
category: tool_misuse
pattern: "`-q` 被叠加成 `-qq`：pytest 静默掉 `N passed` 摘要行，导致下游解析器拿不到用例总数而报出 total=0"
root_cause: |
  `-q` 是**可叠加**的计数型开关。当 `pyproject.toml` 的 `addopts` 里已经写了 `-q`，命令行再补一个
  `-q` 时就变成 `-qq`；在更高的静默级别下，pytest 不再打印末行的
  `N passed / M failed` 摘要，只剩逐用例的进度点。

  下游的测试率解析器按摘要行取用例总数，取不到就落成 `total=0`。而"通过率"是按
  `passed / total` 计算的，分母为 0 时被处理成满分，于是最终输出 `rate=1.0, total=0`——
  **一个分母为零却报 100% 的假绿信号**。

  这是纯确定性的行为：同样的 addopts + 同样的命令行必然产生同样的静默级别，因此症状稳定复现，
  不会"时好时坏"。
detection_trigger: |
  - 验证命令输出 `rate=1.0, total=0`：通过率满分但用例总数为零，两者互相矛盾
  - 捕获的 `pytest -q` 输出只有进度点（`.` / `F`），没有末行 `N passed` 摘要
  - 把静默级别降一级（去掉一个 `-q`）后摘要行立刻回来、total 恢复正常
fix_template: |
  1. 供解析的命令去掉 `-q`，保留摘要行——解析器只依赖末行摘要，不需要静默。
  2. `addopts` 与命令行避免重复用同一个计数型开关（`-q` 会被叠加成 `-qq`）；二选一即可。
  3. 解析器把 `total=0` 视为**测量失败**而不是满分：分母为零时不得报 100%，应报 `unknown` 并
     回显原始输出片段，让"无摘要"与"零用例"两种情况可区分。
  4. 解析失败时打印捕获到的原始输出（或至少其末若干行），使静默级别问题可自证。
language: python
tags:
  - pytest
  - test-infra
  - output-parsing
  - false-positive
severity: medium
confidence: 0.85
occurrences: 1
audit_source: EXP-d4339b68b7c5
---

## 详细描述

验证命令报告 `rate=1.0, total=0`——测试通过率 100%，但用例总数是 0。这两个数字互相矛盾：
真实含义不是"全部通过"，而是**根本没解析到用例数**。把 pytest 的捕获输出打出来看，只有一串进度点，
没有末行的 `N passed` 摘要。

原因在静默级别：项目的 `pyproject.toml` 里 `addopts` 已经带了 `-q`，调用方在命令行又补了一个 `-q`，
两者叠加成 `-qq`。pytest 在更高的静默级别下不再输出摘要行，解析器取不到总数，落成 `total=0`；
分母为零的通过率被当成满分，于是产出一个"看起来最健康"的绿色信号。

这一条的危害不在"跑错了测试"，而在**证据被静默替换**：测试可能全部真实执行并通过，也可能大面积
失败，报告都给不出区分——因为承载结论的那一行文字根本没被打印出来。

## 根因链

1. **直接原因**：pytest 拿到的是 `-qq`，摘要行被静默掉。
2. **机制层**：`-q` 是计数型开关（可叠加），`addopts` 与命令行两处的 `-q` 会叠加而非覆盖；
   配置里写死的开关与调用方的习惯性开关缺乏去重，是配置与调用方之间的隐式耦合。
3. **为什么没被发现**：解析器只在**解析成功**的假设下工作——取不到数字就默认 0，而 0 又被
   分母逻辑"消化"成满分，两端各自看起来都合理，错误在交界处被吃掉了。
4. **为什么这是流程缺陷而非个人失误**：把 `-q` 写进 `addopts` 是为了日常开发的可读性，把 `-q`
   写进命令是为了日志简短，两个决定各自都合理；只有当它们服务于"供机器解析"这一第三种用途时，
   叠加出的 `-qq` 才成为缺陷。**供解析的运行与供人看的运行需要不同的参数**，这一点没有被显式区分。

## 代码示例

### ❌ 错误示例

```toml
# pyproject.toml —— 配置里已有 -q
[tool.pytest.ini_options]
addopts = "-q --strict-markers"
```

```bash
# 调用方再补一个 -q → 实际生效的是 -qq，摘要行被静默
pytest -q tests/ 2>&1 | tee pytest.log

# pytest.log（节选）：只有进度点，没有 "N passed"
# ....................................
```

```python
# 解析器：取不到总数就当 0，再被分母逻辑变成满分
def test_rate(output: str) -> dict:
    m = re.search(r"(\d+) passed", output)
    total = int(m.group(1)) if m else 0        # ← 解析失败与"零用例"不可区分
    return {"rate": 1.0, "total": total}
    #                       ^^^^^^^^^^^ 分母为零仍报 100% → 假绿
```

### ✅ 正确示例

```bash
# 供解析的运行：去掉 -q，保留摘要行
pytest tests/ 2>&1 | tee pytest.log
# pytest.log 末行（摘要行回来了）：
#   N passed in X.XXs
```

```toml
# 或者：需要静默时只在一处给 -q，避免叠加
[tool.pytest.ini_options]
addopts = "--strict-markers"    # 静默级别交给调用方决定
```

```python
# 解析器：把"解析失败"与"零用例"分开，且分母为零不报满分
def test_rate(output: str) -> dict:
    m = re.search(r"(\d+) (?:passed|failed|error)", output)
    if m is None:
        return {                       # 测量失败，不是满分
            "rate": None,
            "total": None,
            "status": "unknown",
            "raw_tail": "\n".join(output.splitlines()[-5:]),   # 回显原始输出
        }
    total = int(m.group(1))
    if total == 0:
        return {"rate": None, "total": 0, "status": "no-tests-collected"}
    return {"rate": passed / total, "total": total, "status": "ok"}
```

## 对应失败模式

**(e) 工具误用（tool_misuse）**：错误的根源在命令行/配置参数的用法——`-q` 被叠加成 `-qq`，属于
"用错了 CLI 参数"，而不是被测代码的运行时行为偏离（`runtime_deviation`），也不是覆盖范围缺失
（`coverage_vacuum`，测试确实执行了）。修复动作也落在参数层面：调整参数、避免两处重复，而不是
补测试或改代码。

**不适用场景（反例）**：若 `total=0` 是因为**测试确实一个都没被收集到**（例如路径写错、`testpaths`
未命中），那问题不在静默级别，本条不适用——先确认去掉 `-q` 后摘要行是否回来，再定性。

**置信度说明**：0.85 —— `addopts` 与命令行叠加是 pytest 的确定性行为，结论不依赖环境差异；
症状（`rate=1.0` 与 `total=0` 同时出现）特征鲜明、几乎不会被误读成别的模式。未给更高分，是因为
本条只有一处现场记录，尚缺"跨项目/跨静默级别"的第二次独立验证。

## 改进方向

- **短期**：把"供机器解析的命令"与"供人阅读的命令"区分开——前者不带 `-q`；解析器把
  `total=0` / 无摘要一律判为测量失败并回显原始输出末几行。
- **长期**：在测试基础设施层固化一条约束——任何计数型开关（`-q`、`-v`）只允许在一处声明，
  并在 CI 中对"通过率满分但总数为零"这类自相矛盾的组合直接判失败，让假绿无法通过闸门。
