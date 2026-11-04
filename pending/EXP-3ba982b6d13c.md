---
adoption_count: 0
category: agent_cp_failure
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: stdd verify run 报 needs_revision 而 pytest tests/ 全绿；对每个 CP 的 -k
  表达式跑 pytest --collect-only -q 命中 0 条
experience_id: EXP-3ba982b6d13c
first_seen: '2026-11-03'
fix_template: 落 CP 前先 collect-only 验证选择器非空；测试函数名必须包含选择器里的每个词（下划线敏感、大小写不敏感、按子串匹配），改名优先于放宽选择器
language: python
last_seen: '2026-11-03'
lifecycle_state: discovered
occurrences: 1
pattern: canonical spec 的 CP 选择器（pytest -k 表达式）与测试函数名不对齐：全量用例绿，verify 仍判 needs_revision（选择器命中
  0 条被当作「断言未执行」）
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: CP 的 -k 表达式在 Gate 2 写下后未与实现期的测试命名对齐；Verify 以「该 CP 选中了几条」作为执行证据，0 条 = 未执行
severity: high
source_change: 2026-11-02-trend-wide-exit-portfolio
source_file: ''
tags:
- pytest
- verify
- selector
- agent-cp
---


