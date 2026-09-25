---
experience_id: EXP-BL-0011
category: contract_gap
pattern: "解密函数的契约是接收**完整加密 XML**（内部自行提取 `<Encrypt>`），调用方误传裸密文导致 XML 解析失败"
root_cause: |
  解密函数的 API 参数名是 `encrypt_xml`，契约是 `<xml><Encrypt>…</Encrypt></xml>`
  这个**整体**；调用方若先自行提取 `<Encrypt>` 内层值再传入，`ET.fromstring` 会对
  裸密文抛 `not well-formed (invalid token)`。

  参数名里的层次信息（`encrypt_xml` 里的 `xml`）没有被读出来：调用方按「encrypt」
  这个词理解为「密文值」，于是多做了一步提取。契约写在参数名与 docstring 里，
  而调用方按自己的理解推断 —— 两者对「这个参数是什么」的认识不同。
detection_trigger: |
  - HTTP 400 `not well-formed (invalid token)`
  - 日志出现「Webhook 解密失败」
  - 检查调用点：传进去的是完整 body，还是已经提取过的密文值
fix_template: |
  1. 调用方传整个 body（含外层包裹 XML），不要自行提取 `<Encrypt>`。
  2. 必要时在函数 docstring 里明确「接收完整加密 XML，而非密文值」——
     把契约写在调用方一定会看到的位置。
language: python
tags:
  - wecom
  - crypto
  - api-contract
  - xml
severity: medium
confidence: 0.80
occurrences: 1
audit_source: EXP-de6fae2a64c2
---

## 详细描述

解密函数负责解开企业微信回调里的密文。它的签名长这样：

```python
def decrypt(self, encrypt_xml: str, ...) -> str:
    ...
```

参数名已经说明了一切：`encrypt_xml` —— 一个**完整加密 XML**，而不是密文值。函数内部
自己解析 XML、找到 `<Encrypt>` 元素、取出内层内容、再解密。也就是说，「提取内层值」
这一步是解密函数的职责。

调用方做了一步多余的提取：先自己从 body 里取出 `<Encrypt>` 的内层密文，再把裸密文
传给 `decrypt`。函数内部照常执行 `ET.fromstring(encrypt_xml)`，而裸密文不是合法的
XML —— 抛 `not well-formed (invalid token)`，请求以 HTTP 400 结束，日志里留下
「Webhook 解密失败」。

从错误信息很难直接看出问题所在：`not well-formed (invalid token)` 描述的是「输入不是
合法 XML」，而调用方确信自己传的就是一段从 XML 里取出来的内容 —— 它不会想到问题在于
**自己不该做那次提取**。

## 根因链

1. **现象层**：HTTP 400 `not well-formed (invalid token)`，日志报 Webhook 解密失败。
2. **直接原因**：调用方把裸密文传给了期待完整 XML 的 `decrypt`。
3. **为什么会多提取一步**：参数名 `encrypt_xml` 被按 `encrypt` 理解成了「密文值」。
   调用方在别处（验签、回包）都直接与密文值打交道，于是自然认为「解密函数的输入当然
   是密文值」—— 这一步推断是合理的，只是与函数的真实契约不符。
4. **本质原因**：契约的**层次**只写在参数名里，而参数名是自然语言的一部分，可被合理
   误读。函数内部对输入做了解析（`ET.fromstring`），这意味着它对输入的**形状**有
   强要求；但这条要求没有在任何调用方一定会看的地方被声明。当契约只靠命名传达时，
   调用方按语义推断出的层次就可能与实现的层次不同 —— 这与 EXP-BL-0010 属同一族：
   回调集成里「哪个参数作用于哪一层」没有被显式登记。

## 代码示例

### ❌ 错误示例

```python
def handle_callback(body: str, msg_signature: str, ...):
    # ❌ 先自行提取 <Encrypt> 内层值，再传给 decrypt
    root = ET.fromstring(body)
    encrypt_value = root.find("Encrypt").text
    plaintext = crypto.decrypt(encrypt_value)       # ❌ 契约要的是完整 XML
    # → ET.fromstring("裸密文") → ParseError: not well-formed (invalid token)
    # → HTTP 400，日志：Webhook 解密失败
```

### ✅ 正确示例

```python
def decrypt(self, encrypt_xml: str, ...) -> str:
    """解密企业微信回调密文。

    参数 encrypt_xml 接收**完整的加密 XML**（形如
    ``<xml><Encrypt>…</Encrypt></xml>``），而非密文值 —— 函数内部自行提取
    ``<Encrypt>`` 的内层内容。调用方请勿预先提取。
    """
    root = ET.fromstring(encrypt_xml)        # ✅ 期待整体，层次与契约一致
    encrypt_value = root.find("Encrypt").text
    return self._decrypt_value(encrypt_value, ...)


def handle_callback(body: str, msg_signature: str, ...):
    # ✅ 调用方直接传整个 body（含外层包裹 XML）
    plaintext = crypto.decrypt(body)
```

```python
# ✅ 用例：把契约的两个层次都钉住，避免下次又被误读
def test_decrypt_accepts_whole_xml_rejects_bare_ciphertext():
    xml = f"<xml><Encrypt><![CDATA[{CIPHER}]]></Encrypt></xml>"
    assert decrypt(xml, ...) == EXPECTED_PLAINTEXT          # ✅ 整体可用

    with pytest.raises(ET.ParseError):
        decrypt(CIPHER, ...)                                # ✅ 裸密文明确失败
```

第二条断言看起来在「测试失败路径」，但它是这条契约唯一可靠的表达方式：只有让「传裸
密文」这件事在测试里明确失败，调用方才不会再次按 `encrypt` 这个词去推断参数含义。

## 对应失败模式

**(k) 契约断层（contract_gap）**：函数与调用方对 `encrypt_xml` 这个参数的**层次**
理解不一致 —— 函数按「完整 XML」实现（内部解析），调用方按「密文值」使用（预先提取）。
两侧对同一个参数的认识不同，且差异不会被类型检查发现（两边都是 `str`），只在运行时
表现为一个描述输入形状的解析错误。归到 contract_gap 而不是 runtime_deviation，是因为
运行时的偏离只是表征；根因是参数契约的层次没有被显式声明，两侧各按自己的理解行事。
本条与 EXP-BL-0010（签名对象是内层值还是整个 body）属同一族：回调集成的契约层次
问题，一处错在「该取内层却取了整体」，一处错在「该传整体却传了内层」—— 方向相反，
本质相同。

**置信度说明**：给 0.80。源记录把契约说得很明确（参数名 `encrypt_xml`、内部
`ET.fromstring`、错误信息 `not well-formed (invalid token)`），据此可以精确写出
修复与用例；且给出的修法成本极低（补一句 docstring 就能防止再犯），可操作性高。
未给更高分是因为源记录只记了 1 次发生，且本条与 EXP-BL-0010 同族、同源改动，
两条合并看仍只是一次集成事故的两个侧面，独立样本面较窄。

## 改进方向

**短期**：
- 修正所有调用点：传完整 body，删掉调用方自行的 `<Encrypt>` 提取步骤。
- 在解密函数的 docstring 里写明「接收完整加密 XML，而非密文值」—— 这条声明的成本
  极低，而它正好覆盖了参数名容易被误读的那一层。
- 补一条双向用例：整体 XML 可用、裸密文明确抛解析错误。

**长期**：
- 为回调集成里的每个参数登记「作用于哪一层」（整体 / 元素内层 / 解密后明文），
  写进函数注释或接口文档。EXP-BL-0010 与本条是同族缺陷的两个方向，说明只靠命名
  传达层次是不够的。
- 让契约在类型上可见：能用新类型（如 `EncryptedXml` 与 `CipherText` 两个不同的包装
  类型）表达层次的，就不要都用 `str` —— 两边都是 `str` 是本类缺陷能长期潜伏的直接
  原因。
- 集成评审清单加一项：凡参数名里含 `xml` / `raw` / `body` / `value` 这类词的位置，
  逐一确认调用方传的层次与实现期待的层次是否一致。
