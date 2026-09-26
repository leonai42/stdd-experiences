---
category: contract_gap
confidence: 0.5
detection_trigger: dt
experience_id: EXP-ps20
first_seen: '2026-01-01'
fix_template: ft
language: python
last_seen: '2026-01-01'
lifecycle_state: packaged
occurrences: 1
pattern: p
provenance: ai-inferred
provenance_weight: 0.6
root_cause: rc
severity: medium
source_change: manual
source_file: ''
tags: []
audit:
  audited_on: '2026-09-26'
  audit_commit: 62b73cf
  verdict: reject
  bucket: E_拒绝_测试夹具
  reason: '占位符 / 测试数据泄漏，非真实经验'
  detail: '全字段为二字母占位（pattern=p / root_cause=rc / fix_template=ft / detection_trigger=dt），tags 为空，正文为字面量 body —— 夹具记录'

---

body
