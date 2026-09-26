---
adoption_count: 0
category: content_quality
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: verify 完成行 aligned 与 失败 同时非零且视觉矛盾（如 aligned:38 | 失败:38）
experience_id: EXP-9e11d934db0d
first_seen: '2026-08-26'
fix_template: 汇总按 contract_audit_status 四态统计（aligned/needs_revision/invalid/unknown），success
  单列为「适配器未执行」独立诊断
language: python
last_seen: '2026-08-26'
lifecycle_state: discovered
occurrences: 1
pattern: 'verify 汇总行「失败: N」按适配器 success 计数；unknown 经测试覆盖推断为 aligned 的场景 success=False
  → 打印「aligned: 38 | 失败: 38」自相矛盾，误导 Gate 3 报告'
project_type: toolchain
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 把适配器能否自动执行场景（success）当作契约失败数；contract_audit_status 四态才是审计判定
severity: low
source_change: 2026-08-26-kanyu-retro-toolchain
source_file: ''
tags:
- verify
- reporting
- gate
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


