---
experience_id: EXP-BL-0010
category: contract_gap
pattern: "企业微信回调签名的对象是 `<Encrypt>` 内层值而不是整个 XML body；测试 helper 若对整个 body 签名，会误导实现"
root_cause: |
  企业微信协议：`msg_signature = SHA1(sorted(token, timestamp, nonce, encrypt_value))`，
  其中 `encrypt_value` 是 `<Encrypt>` 元素**内部**的内容，不是整个 XML body。

  测试若对整个 body 签名，实现与测试就在**自洽中共同偏离真实协议**：两边用同一个错误
  的 helper，于是签出来的结果彼此校验通过、单元测试全绿，而真实平台按协议用内层值
  签名，校验必然失败。测试在这里不仅没有覆盖协议，还起到了掩盖作用 —— 它把「实现与
  测试一致」伪装成了「实现与协议一致」。
detection_trigger: |
  - 真实企业微信推送被 403 拒绝，而单元测试全绿（自洽性掩盖了协议偏差）
  - 检查签名 helper：它是对整个 body 做 SHA1，还是先从 XML 里取出 `<Encrypt>` 内层值
fix_template: |
  1. 签名实现与测试 helper 都必须先从 XML body 提取 `<Encrypt>` 内层值，再对其签名。
  2. 集成测试用真实协议格式构造 body（外层 XML 包裹 `Encrypt`），不要用一个「简化过」
     的内部格式；否则测试与实现同样自洽地偏离协议。
language: python
tags:
  - wecom
  - callback
  - signature
severity: high
confidence: 0.85
occurrences: 1
audit_source: EXP-4fec447d4460
---

## 详细描述

企业微信回调的签名算法对「签什么」有明确规定：

```
msg_signature = SHA1(sorted(token, timestamp, nonce, encrypt_value))
```

关键在这个 `encrypt_value` —— 它是回调 body 里 `<Encrypt>` 元素的**内部内容**，
不是整个 XML body。回调 body 的形状是：

```xml
<xml>
  <ToUserName>...</ToUserName>
  <Encrypt>密文值</Encrypt>
  <AgentID>...</AgentID>
</xml>
```

签名对象是「密文值」这一层，而整个 body（含 `<xml>`、`<ToUserName>`、`<AgentID>` 等）
是它外面的包裹。

缺陷形态是：**测试 helper 对整个 body 签名**。实现方拿到这个 helper 当参照，也照着签
整个 body；于是两边算出同一个（错误的）签名，单元测试全部通过。真实企业微信按协议用
内层值签名并推送过来 —— 校验失败，返回 403。

这条经验的核心不是「签名写错了」，而是**测试在这里扮演了合谋者的角色**：错误被实现
与测试双方共同持有并互相确认，测试套件全绿反而成了「协议一致性已经验证过」的假证据。

## 根因链

1. **现象层**：真实推送被 403 拒绝，单元测试全绿。
2. **直接原因**：签名对象取错层级 —— 用了整个 XML body，而不是 `<Encrypt>` 内层值。
3. **为什么测试没发现**：测试 helper 与实现犯了同一个错。签名是「两侧用同一算法算出
   同一个值」的校验，因此只要双方用同一个 helper，任何错误都对内自洽。测试对协议的
   依赖被替换成了对 helper 的依赖 —— helper 是双方共用的，于是没有任何一处代表真实
   协议。
4. **本质原因**：**协议的三方校验被降维成了两方校验**。真实协议校验需要三方在场：
   平台（按协议签名）、实现（按协议验签）、测试数据（真实协议格式的 body）。当测试
   数据不是真实格式、且签名使用共用的 helper 时，平台这一方就被移出了校验，剩下的
   双方必然一致。破解方式因此只有一条：让测试数据带上真实协议的形状（外层 XML 包裹
   `Encrypt`），使「取错层级」这件事在测试里也必然失败。

## 代码示例

### ❌ 错误示例

```python
# 测试 helper：对整个 body 签名
def make_signature(token, timestamp, nonce, body: bytes) -> str:
    # ❌ 签的是整个 body，而不是 <Encrypt> 内层值
    raw = "".join(sorted([token, str(timestamp), nonce, body.decode()]))
    return hashlib.sha1(raw.encode()).hexdigest()


# 实现：照抄了 helper 的做法
def verify_signature(token, timestamp, nonce, body: bytes, msg_signature: str) -> bool:
    expected = make_signature(token, timestamp, nonce, body)   # ❌ 同一个错误
    return hmac.compare_digest(expected, msg_signature)


# 测试：用同一个 helper 造签名 → 必然通过
def test_verify_signature_ok():
    body = b"<xml><Encrypt>cipher</Encrypt></xml>"
    sig = make_signature(TOKEN, TS, NONCE, body)
    assert verify_signature(TOKEN, TS, NONCE, body, sig) is True   # 绿，但协议不符


# 真实推送：平台按协议对 <Encrypt> 内层值签名 → 403
```

### ✅ 正确示例

```python
import xml.etree.ElementTree as ET


def extract_encrypt(body: bytes) -> str:
    """从完整回调 XML 中取出 <Encrypt> 元素的内层内容。"""
    root = ET.fromstring(body)
    node = root.find("Encrypt")
    if node is None or node.text is None:
        raise ValueError("malformed callback body: missing <Encrypt>")
    return node.text


def make_signature(token, timestamp, nonce, body: bytes) -> str:
    # ✅ 先提取内层值，再对 (token, timestamp, nonce, encrypt_value) 排序后签名
    encrypt_value = extract_encrypt(body)
    raw = "".join(sorted([token, str(timestamp), nonce, encrypt_value]))
    return hashlib.sha1(raw.encode()).hexdigest()


def verify_signature(token, timestamp, nonce, body: bytes, msg_signature: str) -> bool:
    expected = make_signature(token, timestamp, nonce, body)
    return hmac.compare_digest(expected, msg_signature)


# ✅ 集成测试用真实协议格式构造 body：外层 XML 包裹 Encrypt
#    （不是简化过的内部格式 —— 简化格式会让测试与实现同样自洽地偏离协议）
REAL_SHAPED_BODY = (
    b"<xml>"
    b"<ToUserName><![CDATA[<corp_id>]]></ToUserName>"
    b"<Encrypt><![CDATA[cipher_value]]></Encrypt>"
    b"<AgentID><![CDATA[<agent_id>]]></AgentID>"
    b"</xml>"
)


def test_signature_covers_inner_encrypt_value_only():
    sig = make_signature(TOKEN, TS, NONCE, REAL_SHAPED_BODY)
    # ✅ 与「对内层值签名」的独立计算一致
    independent = hashlib.sha1(
        "".join(sorted([TOKEN, str(TS), NONCE, "cipher_value"])).encode()
    ).hexdigest()
    assert sig == independent

    # ✅ 反向对照：把外层包裹改动一点，签名不应变化（证明签名对象只是内层值）
    mutated = REAL_SHAPED_BODY.replace(b"<agent_id>", b"<other_id>")
    assert make_signature(TOKEN, TS, NONCE, mutated) == sig


def test_signature_rejects_whole_body_signature():
    body_sig = hashlib.sha1(
        "".join(sorted([TOKEN, str(TS), NONCE, REAL_SHAPED_BODY.decode()])).encode()
    ).hexdigest()
    # ✅ 按整个 body 签出来的值必须验签失败 —— 这条用例专门拦住那个错误的 helper
    assert verify_signature(TOKEN, TS, NONCE, REAL_SHAPED_BODY, body_sig) is False
```

最后一条反向对照是本模式的要害：只证明「正确的签名能通过」并不足以发现层级取错，
必须同时证明「错误层级的签名不能通过」，才能把协议的三方校验补回来。

## 对应失败模式

**(k) 契约断层（contract_gap）**：这里是本系统与第三方平台（企业微信）之间的接口契约
断层 —— 契约规定签名对象是 `<Encrypt>` 内层值，实现的验签对象是整个 XML body。两侧
对同一参数 `msg_signature` 的计算基准不同，且这个差异在**实现与测试双边自洽**的情况下
完全不可见。归到 contract_gap 而不是 hallucination，是因为这里没有凭空发明 API：签名
算法、参数名、排序规则都是真实协议里就有的，错的是「对哪个层次的数据应用它」——
契约的层次没有被对齐，而不是契约被虚构。

**置信度说明**：给 0.85。源记录把协议层次说得非常清楚（`msg_signature = SHA1(sorted
(token, timestamp, nonce, encrypt_value))`，并明确指出 `encrypt_value` 是 `<Encrypt>`
元素内部内容），据此可以直接写出正确的签名与一条能拦住错误 helper 的反向对照用例；
「实现与测试在自洽中共同偏离真实协议」这一洞察通用性很强，适用于所有使用共享签名
helper 的第三方回调集成。未给更高分是因为源记录只记了 1 次发生；且测试侧的修复需要
构造真实协议格式的 body，在缺少平台沙箱的环境里只能靠手工构造（本条的示例即为此形态），
无法完全依赖真实回调回放。

## 改进方向

**短期**：
- 修正签名实现与测试 helper：两者都先从 XML body 提取 `<Encrypt>` 内层值再签名；
  确保没有第二份「对整个 body 签名」的实现残留（包括文档里的示例代码）。
- 把集成测试的 body 换成本条示例中的真实协议格式（外层 XML 包裹 `Encrypt`），
  并补一条「按整个 body 签名必须验签失败」的反向对照用例。
- 复查同一集成里其他与协议层次相关的取值（解密输入、回包加密、时间戳与 nonce 的来源），
  这类「取哪一层」的错误通常成组出现。

**长期**：
- 为第三方回调建立一条独立的契约测试：用**真实协议格式**的样本数据（而非自造格式）
  驱动签名与解密，使平台这一方始终留在校验里。凡是平台缺席的校验，都只能证明双边自洽。
- 确立纪律：签名 / 加解密类的测试 helper 与被测实现不得共用同一份计算代码。至少要让
  helper 的输入数据形态与真实协议一致，否则测试只是把实现里的错误复述了一遍。
- 把「取错层级」纳入集成评审清单：对接第三方协议时，逐项确认每个参数作用于哪一层
  （整体 / 元素内层 / 解密后的明文），并在代码注释里写明该层次 —— 层次是本类缺陷唯一
  的着落点。
