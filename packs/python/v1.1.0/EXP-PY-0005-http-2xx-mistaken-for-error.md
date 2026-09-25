---
experience_id: EXP-PY-0005
category: contract_gap
pattern: "HTTP 客户端按「状态码 != 200 即错误」判定，把 2xx 家族里的成功响应（如 202 Accepted）连同 body 一起降级成错误：业务成功码根本读不到，症状与「真正的失败」逐字相同（同一处失败日志、同一份失败计数）"
root_cause: |
  公共请求层的判据写的是 status_code != 200（而非 2xx 区间），且非 200 分支丢弃 body
  —— 业务码与传输码混为一谈。

  把「相等」当成「区间」是一个具体的判定缺陷，但它引发的后果不是「少判了一种情况」，
  而是**成功响应被归类为失败**：调用方于是看到一个语义完全向反的结论，而且这个结论
  与真实失败共享同一套日志与计数，从输出侧无法区分。
detection_trigger: |
  - 接口文档写明成功响应是 202/204，而该调用点 100% 失败
  - 失败码是本地拼的 HTTP 码，不是对方系统返回的业务码
  - 修掉一个失败原因后失败率毫无变化（说明还有第二个原因被同一症状掩盖）
fix_template: |
  1. 判定改 not (200 <= sc < 300)
  2. 非 2xx 才降级为 {code: HTTP码}
  3. 为 200 / 202 / 非 2xx / 非 JSON 四种各写用例
  4. 部署后必须读回对方系统的真值，不能只信下发路径的自述（自述会被同一 bug 污染）
language: python
tags:
  - http
  - status-code
  - contract
  - error-classification
  - 202
severity: high
confidence: 0.85
occurrences: 1
audit_source: EXP-98910b78ea70
---

## 详细描述

公共请求层用「状态码是否等于 200」来判定成败，而不是「是否落在 2xx 区间」，并且非 200 分支直接把 body 丢掉、只回填一个本地拼的 HTTP 码。

后果有两层：

1. **成功被读成失败**：接口文档写明成功响应是 HTTP 202，而 202 != 200，于是这个成功响应连同 body 一起被降级成错误对象。业务成功码根本没有机会被读到。
2. **与真实失败不可区分**：被降级后的错误，与「真正的失败」走同一处失败日志、计入同一份失败计数。也就是说，症状是**逐字相同**的，从输出侧无法分辨「业务真的失败了」和「业务成功了但被判定逻辑吞掉了」。

实盘证据：下发函数对 11 个标的全部失败，失败码 `<broker_code>`（一个与参数校验相关的真实业务错误）是**真的**对方系统响应；而这个真实失败又**掩盖了紧随其后的第二个 bug** —— 成功响应是 HTTP 202，被公共请求层当成错误吞掉。两个 bug 叠加时，只修其中任何一个，症状都不变（仍然是 0/11）。这解释了 detection_trigger 里那条最关键的信号：**修掉一个失败原因后失败率毫无变化**。

## 根因链

1. **现象层**：下发动作 100% 失败，失败码来自本地拼的 HTTP 码而非对方业务码。
2. **直接原因**：判据写成 `status_code != 200`，把「成功」定义成了一个点而不是一个区间；非 200 分支丢弃 body，连事后补救的线索也一并丢掉。
3. **为什么难定位**：真实失败先暴露（`<broker_code>`），它提供了一个**看起来完整**的解释，让人停止追查；而被它掩盖的那个 bug（202 被当错误）只在真实失败被修掉之后才可见。两个 bug 的症状完全相同，因此「修一个看变化」成了唯一的区分手段，而这一步在只修一个 bug 时给出的结论是「没修好」。
4. **本质原因**：**业务码与传输码混为一谈**。传输层只应回答「这次 HTTP 交互是否完成」，业务层回答「这次操作是否成功」。把传输层的单点值（200）当作业务成功的充分条件，等于让传输层的实现细节（对方系统选择用 202 表示「已接受」）直接决定业务判定结果 —— 这是契约理解上的断层，不是单纯的边界写错。

## 代码示例

### ❌ 错误示例

```python
def request(path: str, params: dict | None = None) -> dict:
    resp = client.post(path, json=params)
    # ❌ 把「成功」当成一个点；202 Accepted 会被判为失败
    if resp.status_code != 200:
        # ❌ 丢弃 body，业务码再也读不到
        return {"code": resp.status_code, "data": None}
    return resp.json()
```

### ✅ 正确示例

```python
def request(path: str, params: dict | None = None) -> dict:
    resp = client.post(path, json=params)
    # ✅ 成功是一个区间
    if not (200 <= resp.status_code < 300):
        # 只有在传输层确实失败时才降级，且失败码明确标为 HTTP 码
        return {"code": resp.status_code, "data": None, "error_kind": "http"}
    try:
        payload = resp.json()
    except ValueError:
        # 非 JSON：单独一类，不与「业务失败」混同
        return {"code": resp.status_code, "data": None, "error_kind": "non_json"}
    return payload   # ✅ 业务码原样透出，由调用方按业务白名单判定


# 四种情况各写一条用例：200 / 202 / 非 2xx / 非 JSON
def test_202_is_success(fake_client):
    fake_client.returns(status=202, json={"code": 0})
    assert request("/action")["code"] == 0

def test_non_2xx_is_downgraded(fake_client):
    fake_client.returns(status=400, json={"code": "<broker_code>"})
    assert request("/action")["error_kind"] == "http"
```

## 对应失败模式

**(k) 契约断层（contract_gap）**：接口契约（文档）声明成功响应包含 202，而实现侧按 `status_code != 200` 判定成功，两侧对「成功」的定义不一致；且失败分支丢弃 body，使业务码这一契约载体在失败路径上彻底缺席。契约断层在这里表现为「实现与文档各说一套，且实现侧把不一致隐藏在了与真实失败相同的症状里」。

**置信度说明**：0.85。有实盘证据（11 个标的全部失败、双 bug 叠加、单修无效），这是最强的证据类型；`not (200 <= sc < 300)` 是明确可测的区间契约，修复方向无歧义。未给更高分是因为 `occurrences: 1`，且第二个 bug（202 被吞）是在修掉第一个 bug 之后才被观测到的，属于叠加场景下的单次观测。

## 改进方向

- **短期**：所有 HTTP 成败判定统一改为 2xx 区间判定（`not (200 <= sc < 300)`）；非 2xx 才降级，并在降级对象上标明 `error_kind`，把「传输层失败」与「业务失败」在数据结构上分开。
- **短期**：为 200 / 202 / 非 2xx / 非 JSON 四种情况各写用例；失败降级时保留原始 body（或至少保留可解析出的业务码），不要把线索也一起丢掉。
- **长期**：部署后必须**读回对方系统的真值**来验收，不能只信下发路径的自述 —— 自述会被同一个 bug 污染，这正是本次双 bug 叠加能存活到实盘的原因。
- **长期**：在评审清单中加入一条「叠加故障检验」：当一个失败被解释清楚时，追问「修掉它之后失败率会变吗」，用以发现被同一症状掩盖的第二个原因。
