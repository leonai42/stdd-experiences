---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 验证规格里存在 source_contains / 部署后 grep 的字面量判据，而对应测试只断言了结构特征（字段名、数值、或
  token 的一个片段）
experience_id: EXP-b0d55ec9b227
first_seen: '2026-10-12'
fix_template: ① 把契约里的字面量**逐字**搬进断言（token 本身也断言，不只断言它旁边的数值）；② 用变异检查验证这条断言会红（把 token
  换成一个同义串）；③ 若字面量确实要改，走登记通道改契约，而不是让实现先漂移、事后追认
language: python
last_seen: '2026-10-12'
lifecycle_state: discovered
occurrences: 1
pattern: 测试断言的是实现那条日志的**自选子串**（如某个字段名），而规格与验证规格把同一个交付判据钉成**冻结字面量**（用于部署后 grep）—— 于是实现把
  token 换成同义文案，测试照样全绿，冻结判据在生产日志里永远 grep 不到，「修复是否生效」失去锚点
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests/test_cross_leg_ledger.py::test_tc_clc_011a_full_close_logs_three_fields_before_deleting
root_cause: 断言由实现者书写，而实现者会不自觉地把「我实现出来的东西」当作判据；冻结字面量与实现的用词不同时，测试不会替契约说话
severity: high
source_change: 2026-10-11-cross-close-leg-completion
source_file: ''
tags:
- test-vacuity
- frozen-literal
- delivery-predicate
- verification
- log-anchor
---



