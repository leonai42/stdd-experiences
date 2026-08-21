---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: HTTP 400 'not well-formed (invalid token)'，日志 Webhook 解密失败
experience_id: EXP-de6fae2a64c2
first_seen: '2026-08-21'
fix_template: 调用方传整个 body（含外层包裹 XML）；必要时在函数 docstring 明确『接收完整加密 XML 而非密文值』
language: python
last_seen: '2026-08-21'
lifecycle_state: discovered
occurrences: 1
pattern: WeComCrypto.decrypt 契约：接收完整加密 XML（内部提取 Encrypt），调用方误传裸密文导致 XML 解析失败
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: decrypt API 签名参数名为 encrypt_xml，契约是 <xml><Encrypt>…</Encrypt></xml> 整体；调用方若先自行提取
  Encrypt 内层值再传入，ET.fromstring 对裸密文抛 not well-formed
severity: medium
source_change: 2026-08-21-wecom-gateway
source_file: ''
tags:
- wecom
- crypto
- api
---


