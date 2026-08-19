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
---


