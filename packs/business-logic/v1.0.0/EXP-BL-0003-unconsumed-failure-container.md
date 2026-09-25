---
experience_id: EXP-BL-0003
category: contract_gap
pattern: "下发链算出了失败容器（形如 `summary['<item>_failed']` / `failed` 列表），但从未被 HTTP 响应或 UI 消费 —— 部分失败被整体 200 掩盖，用户以为「已生效」"
root_cause: |
  失败容器只被用于写日志。下发入口返回的是状态快照（snapshot）而不是各个回调的结果，
  通知回调丢弃了下游回调的返回值，于是调用方（Flask 路由）拿不到「本次下发哪些环节
  失败」这个信息 —— 信息在链路上被逐段丢掉，最后只剩日志里有。

  结果 UI 只能依据一个 `success` 布尔量判定成败，而这个布尔量表达的是「校验 + 落盘
  成功」，与「下游各环节是否真的生效」完全不是同一件事。两个不同的语义共用了一个
  字段，谁也没发现它们不等价。
detection_trigger: |
  - grep 下发 / 批量操作返回的失败容器，看有谁消费它；若只有 logger 引用它，
    那么任何部分失败都不会到达用户
  - 检验方法：把其中一项注入失败，看 UI 是否仍报成功
  - 断言「注入单项失败 → 响应体含该项 → UI 不显示『已生效』」的用例是否存在
fix_template: |
  1. 让失败容器沿调用链上行：下游回调返回值 → 下发入口 → HTTP 响应体，
     逐段都不许丢弃或降级为日志。
  2. UI 对含 `failed` 非空的结果降级为警告态，并逐条列出失败项，
     不得显示「已生效」。
  3. 补断言用例：注入单项失败 → 响应体含该项 → UI 不显示「已生效」。
language: python
tags:
  - partial-failure
  - failure-as-success
  - atomic-apply
  - ui-honesty
  - leverage
severity: high
confidence: 0.85
occurrences: 1
audit_source: EXP-29f917ebe3e5
---

## 详细描述

一次批量下发（配置 / 杠杆分配一类需要对每个目标逐项生效的操作）的链路上，下游确实
算出了失败容器：进入 `summary` 的 `<item>_failed` 列表，逐项记录了哪些目标没有生效。
这个容器是**正确的、完整的** —— 缺陷不在它的内容，而在它的**去向**。

它没有去向。整条链上唯一读它的地方是 logger。于是：

- 回调层把下游返回值丢掉，只把结果写进日志；
- 下发入口返回的是状态快照（本次操作后的状态），不是「每个目标各自的结果」；
- HTTP 调用方（Flask 路由）拿到的响应体里不含任何失败信息，只有一个 `success`；
- UI 依据 `success` 渲染，显示「已生效」。

用户看到的是「已生效」，实际发生的是「校验通过、状态落盘成功、但有一部分目标没生效」。
这是对外报告口径的直接失真：生产者知道、日志知道、用户不知道。

## 根因链

1. **现象层**：批量下发中部分目标失败，UI 仍报「已生效」；失败项只出现在服务端日志里。
2. **直接原因**：失败容器没有消费者。它在链路上被算出来，然后被丢掉。
3. **为什么很难发现**：链路每一段单看都是「合理」的 —— 回调把结果写进日志属于尽职，
   下发入口返回快照看起来信息更全，路由只传 `success` 也符合「简洁响应」的直觉。
   缺陷存在于**段与段之间**：没有一处规定「失败容器必须逐段上行」，因此每一段都可以
   自行决定不传，且不会有人因此变红。
4. **本质原因**：`success` 这个字段承担了两个不相容的语义 —— 「校验 + 落盘成功」与
   「下游已全部生效」。只有当某个字段同时被两侧按不同含义使用时，部分失败才可能被
   整体 200 掩盖。修法是让两个语义分开表达（各自一个字段），而不是把 `success`
   的判定改得更严 —— 后者会让「落盘成功但下游失败」变成「整体失败」，同样不真实。

## 代码示例

### ❌ 错误示例

```python
def notify_subscribers(targets, payload):
    failed = []
    for target in targets:
        ok = push_to_target(target, payload)      # 逐项结果
        if not ok:
            failed.append(target.id)
    if failed:
        logging.warning("partial failure: %s", failed)   # ❌ 唯一的消费者是日志
    return None                                          # ❌ 不向上返回失败容器


def apply_config(payload):
    config = validate(payload)
    save(config)                                          # 校验 + 落盘
    notify_subscribers(config.targets, payload)            # ❌ 返回值被丢弃
    return {"success": True, "config": config.snapshot()}  # ❌ 只有快照，没有 failed


# Flask 路由：响应体里没有任何失败信息
@app.post("/<prefix>/api/apply")
def apply_route():
    return apply_config(request.json)      # ❌ 部分失败 → 整体 200 + success=True
```

### ✅ 正确示例

```python
def notify_subscribers(targets, payload):
    failed = []
    for target in targets:
        ok = push_to_target(target, payload)
        if not ok:
            failed.append(target.id)
            logging.warning("target push failed: %s", target.id)
    return {"failed": failed}             # ✅ 结果沿调用链上行，不再只进日志


def apply_config(payload):
    config = validate(payload)
    save(config)
    outcome = notify_subscribers(config.targets, payload)     # ✅ 接住返回值
    failed = outcome["failed"]
    return {
        # ✅ 两个语义各自一个字段，不再共用一个 success
        "applied": not failed,
        "persisted": True,
        "failed": failed,
        "config": config.snapshot(),
    }


@app.post("/<prefix>/api/apply")
def apply_route():
    result = apply_config(request.json)
    status = 200 if result["applied"] else 207     # ✅ 部分失败不冒充整体成功
    return jsonify(result), status
```

前端对应的契约：拿到含非空 `failed` 的结果时降级为警告态，逐条列出失败项，并且**不得**
渲染「已生效」。这条必须写成用例，而不是写成 UI 注释。

```python
def test_single_target_failure_is_not_reported_as_applied(client, monkeypatch):
    monkeypatch.setattr(push, "push_to_target", lambda target, payload: target.id != "t-2")

    resp = client.post("/<prefix>/api/apply", json=make_payload())

    assert resp.status_code != 200                 # ✅ 不冒充整体成功
    assert resp.get_json()["failed"] == ["t-2"]    # ✅ 失败项到达响应体
    assert "已生效" not in render_ui(resp.get_json())   # ✅ UI 不显示「已生效」
```

## 对应失败模式

**(k) 契约断层（contract_gap）**：下发链的提供方与消费方对「成功」的契约不一致。提供方
把 `success` 定义为「校验 + 落盘成功」，消费方（UI）把它读作「已全部生效」；而两者之间
本该传递失败信息的通道（失败容器）在链路上被逐段丢弃，于是没有任何一处能把两侧的定义
对齐。这符合契约断层的定义：接口两侧对同一结果的解释不同，且这种不同不会产生任何错误、
警告或异常 —— 只会产生一个看起来正常的 200 响应。归到 contract_gap 而非
content_quality，是因为问题不是「文案措辞不好」，而是**失败信息在数据通路上不存在**。

**置信度说明**：给 0.85。源记录含一条可直接执行的检验（注入单项失败，看 UI 是否仍报
成功），使这个模式可以被自动化验证，而不只是靠人工阅读断言；根因链具名到了具体环节
（回调返回值被丢弃、入口返回快照而非回调结果、路由只能依据布尔量），不是泛泛而谈。
未给更高分是因为源记录只记了 1 次发生，且实际影响面（有多少用户 / 多少次下发真的遇到过
部分失败）未量化，无法判断这一失效在真实使用中被触发的频率。

## 改进方向

**短期**：
- 对所有批量 / 下发类接口做一次「失败容器消费者审计」：grep 每个失败容器的引用点，
  凡只有 logger 引用的，一律把结果沿链路补到响应体。
- 把 `success` 这个字段拆成两个语义字段（如 `persisted` / `applied`），并检查所有
  现有消费方是按哪一个语义在用它 —— 拆分时最容易暴露的就是这类隐藏误读。
- 为每个下发接口补一条「注入单项失败」的用例，断言失败项出现在响应体中且 UI 不显示
  「已生效」。这是本模式唯一的自动化防线。

**长期**：
- 把「部分失败必须显式表达」定为接口约定：批量接口禁止用单一布尔量表达整体结果，
  响应体必须包含逐项结果（成功项 / 失败项各自可枚举）。
- 在 UI 契约层固化三态：全部成功 / 部分失败（警告 + 列出失败项）/ 全部失败。
  把「部分失败」从「成功」里拆出来，是这条约定唯一的落地方式。
- 观测层面：对 `failed` 非空的响应统计比率并设阈值告警。这类失败长期不被发现，
  很大程度上是因为它在监控上完全不可见 —— 全是 200。
