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
---


