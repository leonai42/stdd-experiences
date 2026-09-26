---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 'stdd verify run <change> outputs ''aligned: 0'' with all status=unknown'
experience_id: EXP-0c6a9e2c5d39
first_seen: '2026-08-20'
fix_template: Reconcile verified_by scenarios to aligned after confirming each SC
  is covered by passing TDD tests (test-report evidence); then re-run gate approve
language: python
last_seen: '2026-08-20'
lifecycle_state: discovered
occurrences: 1
pattern: claude_code verify adapter writes contract_audit_status=unknown for all scenarios,
  permanently blocking Gate 3
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: verify adapter cannot auto-assess spec scenario contract alignment; unknown
  is treated as not-verified by _check_gate_verified
severity: medium
source_change: 2026-08-20-data-fix
source_file: ''
tags:
- verify
- gate3
- contract-audit
audit:
  audited_on: '2026-09-26'
  audit_commit: 62b73cf
  verdict: out-of-scope
  bucket: D_建议移出社区池
  reason: '描述的是 STDD 工具链自身实现，下游社区用户无法据此行动'
  note: '非质量拒绝 —— 见解对工具维护者可能有用，故移入 out-of-scope/ 而非 rejected/'
  # 本批 8 条经逐条核对确认通篇为 STDD 工具链内部机制（Gate/change/canon/verify 适配器）；
  # EXP-20e2b6b23fe8 是唯一可争议的一条：它讲的是「子代理的验证结论必须落盘为交付物」，
  # 内核可迁移到任何多代理流程，但记录通篇用 C1/C7/phase-context 的工具链词汇写就，
  # 按 CONTRIBUTING「下游社区用户能否据此行动」判为移出。若日后增设「方法论」主题包，
  # 应复议此条。

---


