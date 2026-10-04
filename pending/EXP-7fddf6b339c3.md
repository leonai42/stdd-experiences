---
adoption_count: 0
category: cross_system_mismatch
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 账本里 result 与 integrity 取值互斥；复位操作之后 reason 与 result 对不上；Gate 3 只读逐场景的
  contract_audit_status 而不读聚合 result —— 于是这个矛盾既不阻塞也不被察觉
experience_id: EXP-7fddf6b339c3
first_seen: '2026-10-04'
fix_template: 复位/重算路径必须把同族的字段一起重算（或抽一个统一的 recompute 入口），并在复位后断言 result 与 integrity
  的一致性；判据不要只读其中一个字段
language: python
last_seen: '2026-10-04'
lifecycle_state: discovered
occurrences: 1
pattern: '同一本账里两个本应同源的字段各自被写，其中一个的写入方漏改了另一个 —— 账本出现「result: aligned」与「integrity: unknown」并存的自相矛盾对'
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 复位路径（stdd verify reset）把观测清掉后重算 result，但没有同步重算 integrity；integrity 停在复位前的旧值。两个字段有各自的写入点，没有一个统一的「账本重算」入口
severity: medium
source_change: 2026-10-04-v406-cc-hook-guard-integrity
source_file: ''
tags:
- v406
- claude-code-integration
- 实测
---

实测：本 change C1.5 first run 用错适配器留下 24 条 SC-* 的 unknown 观测，复位后 result=aligned 而 integrity 仍 unknown，两者并存于 phases.build.verified_by。已如实登记为已知问题（本 change 射程外）。
