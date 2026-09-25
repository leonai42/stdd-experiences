---
experience_id: EXP-PY-0014
category: runtime_deviation
pattern: "HTTP 头的值含非 ASCII 字符（如含中文的 API Key 写进 Authorization 头），请求构造阶段直接抛 UnicodeEncodeError"
root_cause: |
  HTTP 头值在协议层要求 ASCII，httpx 在规范化头值时就按此校验；非 ASCII 的密钥写进
  Authorization 头会直接编码失败。

  而密钥在配置数据层只是一个「字符串」—— 从配置或测试夹具传进来时不带任何编码语义，
  中文或全角字符混入后在数据层完全合法，只有走到协议编码那一步才被拒绝。协议层的
  ASCII 约束与数据层的「字符串即可」之间存在落差，落差无法消除，好在它暴露得足够早。
detection_trigger: |
  - 测试用含中文的 api_key 构造 Authorization 头时抛 'ascii' codec can't encode
  - 更一般的信号：任何请求头值在编码为 ASCII 时失败
  - 关键特征：错误在**任何请求发出前**抛出（无远程副作用）
fix_template: |
  1. 密钥 / 头值只用 ASCII（测试用 sk-test-* 这类纯 ASCII 值）
  2. 实现侧无需转码 —— 约束属于数据，不属于编码路径
  3. 在构造头的位置加 ASCII 前置断言，让违规在配置阶段暴露
language: python
tags:
  - httpx
  - http-header
  - ascii
  - api-key
severity: low
confidence: 0.9
occurrences: 1
audit_source: EXP-7512e8397ae1
---

## 详细描述

HTTP 头字段的值在协议层要求 ASCII。当把含中文（或其它非 ASCII 字符）的 API Key 写进 `Authorization` 头时，请求构造阶段就会抛 `UnicodeEncodeError`（`'ascii' codec can't encode ...`）。触发场景在源记录中很具体：测试用含中文的 `api_key` 去构造 `Authorization` 头。

这个模式与其它编码类缺陷的区别在于**暴露时机**：错误发生在**任何请求发出之前**，没有任何远程副作用，也不会产生静默的错误结论。因此它的严重度是 low —— 属于「廉价错误」：代价是一次立即的异常，而不是一份被污染的远端状态。

值得注意的是修复方向：**实现侧不需要转码**。约束属于数据（密钥本身就该是 ASCII 字符集），不属于编码路径；在请求层加转码只会把非法凭证偷偷送出去，问题会推迟到对方系统才爆发，那才是更糟的形态。

## 根因链

1. **现象层**：构造请求头时抛 `UnicodeEncodeError`，`'ascii' codec can't encode`。
2. **直接原因**：头值含非 ASCII 字符，而头值的规范化要求 ASCII。
3. **为什么会写出非 ASCII 的凭证**：密钥在配置数据层只是一个「字符串」。从配置项或测试夹具传入时不带编码语义，中文、全角字符一旦混入（复制粘贴、占位符直接用了中文），在 Python 的字符串层面完全合法 —— 只有当它被当作**协议头值**编码时，约束才生效。
4. **为什么严重度低**：错误在请求发出前抛出，fail-fast、无远程副作用；「该不该修」不存在歧义（凭证字符集错了就是错了），修复成本也低（换一个 ASCII 值）。
5. **本质原因**：**协议层约束与配置数据层约束之间的落差**。数据层只要求「是字符串」，协议层额外要求「ASCII」。落差本身无法消除，但暴露位置决定了代价 —— 越靠近发出点暴露，代价越低。

## 代码示例

### ❌ 错误示例

```python
# ❌ 密钥里混入了中文（或全角字符）—— 在数据层完全合法
api_key = "密钥-abc123"

headers = {"Authorization": f"Bearer {api_key}"}
client.get("https://example.com/api", headers=headers)
# UnicodeEncodeError: 'ascii' codec can't encode characters in position ...
```

### ✅ 正确示例

```python
# ✅ 密钥 / 头值只用 ASCII（测试夹具同理，用 sk-test-* 这类纯 ASCII 值）
api_key = "sk-test-abc123"


def build_auth_header(api_key: str) -> dict[str, str]:
    # ✅ 前置断言：让违规在配置 / 构造阶段暴露，而不是在请求层
    if not api_key.isascii():
        raise ValueError("api_key must be ASCII (HTTP header values are ASCII-only)")
    return {"Authorization": f"Bearer {api_key}"}


def test_non_ascii_api_key_rejected_before_request():
    with pytest.raises(ValueError):
        build_auth_header("密钥-abc123")   # ✅ 在任何请求发出前被拒绝
```

## 对应失败模式

**(f) 运行时偏离（runtime_deviation）**：预期是「配置里的密钥字符串可直接用于构造请求」（数据层视角），运行时行为是「协议层拒绝该字符串」。两端对「一个合法密钥」的定义不一致，偏离在任何请求发出前就显现 —— 这也是它被归为 low 的原因：偏离是显性的、无副作用的。

**置信度说明**：0.90。头值的 ASCII 要求是 httpx 的确定性行为，不受环境、时序、数据规模影响；错误在任何请求发出前抛出，不产生远程副作用，因此「是否存在偏离」与「该如何修复」都不存在解释空间。未给满分是因为 `occurrences: 1`，且不同 HTTP 客户端对该约束的报错形态可能略有差异（约束本身一致）。

## 改进方向

- **短期**：密钥 / 头值只用 ASCII（测试夹具用 `sk-test-*` 这类纯 ASCII 值）；**实现侧不加转码** —— 约束属于数据而非编码路径。
- **短期**：在构造请求头的位置加 ASCII 前置断言，让违规在配置 / 构造阶段暴露，而不是留给协议层报错。
- **长期**：配置加载时统一校验凭证字段的字符集（如 `isascii()`），把协议约束前移到配置边界，使错误信息能直接指向配置项。
- **长期**：测试夹具中不使用中文占位符表示凭证，避免把「字符串合法」误当成「头值合法」。
