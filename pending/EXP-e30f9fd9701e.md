---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: gate approve --dry-run 后 .stdd.yaml 出现 confirmed_at/confirmed_evidence；或
  'Gate N already confirmed' 出现在未真实确认时
experience_id: EXP-e30f9fd9701e
first_seen: '2026-08-26'
fix_template: 1) 写路径入口统一守卫 dry_run（预检保持只读）；2) _confirm_gate 幂等豁免 dry-run 机器印记——仅当既有
  evidence 含 'dry-run' 时允许 sanctioned CLI 覆盖为真实证据；3) 测试锁定（TC-GATE-108/109）
language: python
last_seen: '2026-08-26'
lifecycle_state: discovered
occurrences: 1
pattern: --dry-run 预检命令仍产生写副作用：gate approve --dry-run 会把 evidence='dry-run-check'
  写入 .stdd.yaml confirmed_evidence（伪造 dialog 审计链），并生成 integration-test.md / Human
  View。后续真实 approve 因幂等短路无法纠正
project_type: toolchain
provenance: ai-inferred
provenance_weight: 0.6
root_cause: cmd_gate 的写路径（_confirm_gate/_auto_generate_human_views）未守卫 args.dry_run；--dry-run
  仅被当作语义提示而非写保护
severity: high
source_change: 2026-08-26-kanyu-retro-toolchain
source_file: ''
tags:
- dry-run
- gate
- audit
- forge
---


